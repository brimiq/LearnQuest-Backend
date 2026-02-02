from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.gamification import Badge, UserBadge, Challenge, Leaderboard, Achievement
from app.services.streak_service import update_user_streak, award_streak_bonus, get_streak_status
from app.utils.decorators import (
    error_response,
    validate_json,
    handle_db_errors,
    validate_query_params,
    APIException
)
import logging

logger = logging.getLogger(__name__)

gamification_bp = Blueprint('gamification', __name__)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _serialize_badges(badges):
    """Serialize a list of badges to JSON-compatible format."""
    return [badge.to_dict() for badge in badges]


def _serialize_challenges(challenges):
    """Serialize a list of challenges to JSON-compatible format."""
    return [c.to_dict() for c in challenges]


# ============================================================================
# BADGE ENDPOINTS
# ============================================================================

@gamification_bp.route('/badges', methods=['GET'])
def get_badges():
    """
    Get all available badges.
    
    Returns:
        - badges: List of all badges
    """
    try:
        badges = Badge.query.all()
        return jsonify({
            'success': True,
            'data': {'badges': _serialize_badges(badges)},
            'count': len(badges)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching badges: {e}")
        return error_response('Failed to fetch badges', 500, 'BADGES_FETCH_ERROR')


@gamification_bp.route('/badges/<int:user_id>', methods=['GET'])
def get_user_badges(user_id):
    """
    Get all badges earned by a specific user.
    
    Args:
        user_id (int): The ID of the user
    
    Returns:
        - badges: List of badges earned by the user
    """
    try:
        # Validate user_id
        if user_id <= 0:
            return error_response('Invalid user ID', 400, 'INVALID_USER_ID')
        
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found', 404, 'USER_NOT_FOUND')
        
        user_badges = UserBadge.query.filter_by(user_id=user_id).all()
        return jsonify({
            'success': True,
            'data': {'badges': [ub.to_dict() for ub in user_badges]},
            'count': len(user_badges)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching user badges: {e}")
        return error_response('Failed to fetch user badges', 500, 'USER_BADGES_ERROR')


# ============================================================================
# LEADERBOARD ENDPOINTS
# ============================================================================

@gamification_bp.route('/leaderboard', methods=['GET'])
@validate_query_params({
    'period': {'type': str, 'allowed': ['daily', 'weekly', 'monthly', 'all_time']},
    'limit': {'type': int, 'min': 1, 'max': 100, 'default': 10}
})
def get_leaderboard():
    """
    Get the user leaderboard.
    
    Query Parameters:
        period (str): Time period filter (daily, weekly, monthly, all_time)
        limit (int): Number of entries to return (1-100, default: 10)
    
    Returns:
        - leaderboard: List of users ranked by XP
        - period: The period filter used
    """
    try:
        period = request.args.get('period', 'all_time')
        limit = request.args.get('limit', 10, type=int)
        
        # Get top users by XP
        if limit < 1:
            limit = 1
        elif limit > 100:
            limit = 100
            
        top_users = User.query.order_by(User.xp.desc()).limit(limit).all()
        
        leaderboard = []
        for i, user in enumerate(top_users, 1):
            leaderboard.append({
                'rank': i,
                'user_id': user.id,
                'username': user.username,
                'avatar_url': user.avatar_url,
                'xp': user.xp,
                'points': user.points
            })
        
        return jsonify({
            'success': True,
            'data': {
                'leaderboard': leaderboard,
                'period': period
            },
            'count': len(leaderboard)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        return error_response('Failed to fetch leaderboard', 500, 'LEADERBOARD_ERROR')


# ============================================================================
# CHALLENGE ENDPOINTS
# ============================================================================

@gamification_bp.route('/challenges', methods=['GET'])
@validate_query_params({
    'active': {'type': bool, 'default': True}
})
def get_challenges():
    """
    Get all challenges, optionally filtered by active status.
    
    Query Parameters:
        active (bool): Filter to active challenges only (default: true)
    
    Returns:
        - challenges: List of challenges
    """
    try:
        active_only = request.args.get('active', 'true').lower() == 'true'
        
        query = Challenge.query
        if active_only:
            query = query.filter_by(is_active=True)
        
        challenges = query.all()
        return jsonify({
            'success': True,
            'data': {'challenges': _serialize_challenges(challenges)},
            'count': len(challenges)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching challenges: {e}")
        return error_response('Failed to fetch challenges', 500, 'CHALLENGES_ERROR')


@gamification_bp.route('/challenges/<int:challenge_id>', methods=['GET'])
def get_challenge(challenge_id):
    """
    Get a specific challenge by ID.
    
    Args:
        challenge_id (int): The ID of the challenge
    
    Returns:
        - challenge: The challenge details
    """
    try:
        # Validate challenge_id
        if challenge_id <= 0:
            return error_response('Invalid challenge ID', 400, 'INVALID_CHALLENGE_ID')
        
        challenge = Challenge.query.get(challenge_id)
        
        if not challenge:
            return error_response('Challenge not found', 404, 'CHALLENGE_NOT_FOUND')
        
        return jsonify({
            'success': True,
            'data': {'challenge': challenge.to_dict()}
        }), 200
    except Exception as e:
        logger.error(f"Error fetching challenge {challenge_id}: {e}")
        return error_response('Failed to fetch challenge', 500, 'CHALLENGE_FETCH_ERROR')


# ============================================================================
# ACHIEVEMENT ENDPOINTS
# ============================================================================

@gamification_bp.route('/achievements', methods=['GET'])
def get_achievements():
    """
    Get all achievements.
    
    Returns:
        - achievements: List of all achievements
    """
    try:
        achievements = Achievement.query.all()
        return jsonify({
            'success': True,
            'data': {'achievements': [a.to_dict() for a in achievements]},
            'count': len(achievements)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching achievements: {e}")
        return error_response('Failed to fetch achievements', 500, 'ACHIEVEMENTS_ERROR')


# ============================================================================
# XP ENDPOINTS
# ============================================================================

@gamification_bp.route('/xp/add', methods=['POST'])
@jwt_required()
@validate_json(required_fields=['xp'])
@handle_db_errors
def add_xp():
    """
    Add XP to the authenticated user's account.
    
    Request Body:
        xp (int): Amount of XP to add (must be positive)
    
    Returns:
        - message: Success message
        - total_xp: Updated total XP
        - xp_added: Amount added
    """
    user_id = get_jwt_identity()
    
    user = User.query.get(user_id)
    if not user:
        return error_response('User not found', 404, 'USER_NOT_FOUND')
    
    data = request.get_json()
    xp_amount = data.get('xp', 0)
    
    # Validate XP amount
    if not isinstance(xp_amount, int):
        return error_response('XP amount must be an integer', 400, 'INVALID_XP_TYPE')
    
    if xp_amount <= 0:
        return error_response('XP amount must be positive', 400, 'INVALID_XP_VALUE')
    
    if xp_amount > 10000:
        return error_response('XP amount cannot exceed 10000 per request', 400, 'XP_LIMIT_EXCEEDED')
    
    # Add XP
    user.xp += xp_amount
    db.session.commit()
    
    logger.info(f"Added {xp_amount} XP to user {user_id}. New total: {user.xp}")
    
    return jsonify({
        'success': True,
        'message': f'Added {xp_amount} XP!',
        'data': {
            'total_xp': user.xp,
            'xp_added': xp_amount
        }
    }), 200


# ============================================================================
# STREAK ENDPOINTS
# ============================================================================

@gamification_bp.route('/streak/update', methods=['POST'])
@jwt_required()
@handle_db_errors
def streak_update():
    """
    Update the user's learning streak.
    
    This endpoint should be called when a user completes a learning activity.
    It will:
    1. Update the streak based on last active timestamp
    2. Award XP and badges for milestone streaks
    
    Returns:
        - streak_days: Current streak count
        - message: Status message
        - total_xp: Updated total XP
        - bonuses: List of awarded bonuses (if any)
    """
    user_id = get_jwt_identity()
    
    user = User.query.get(user_id)
    if not user:
        return error_response('User not found', 404, 'USER_NOT_FOUND')
    
    # Update the streak
    streak_result = update_user_streak(user_id)
    
    if streak_result is None:
        return error_response('Failed to update streak', 500, 'STREAK_UPDATE_FAILED')
    
    # Check for milestone bonuses
    bonuses = award_streak_bonus(user_id, streak_result['streak_days'])
    
    # Get updated user info
    updated_user = User.query.get(user_id)
    
    response = {
        'success': True,
        'data': {
            'streak_days': streak_result['streak_days'],
            'message': streak_result['message'],
            'total_xp': updated_user.xp
        }
    }
    
    if bonuses:
        response['data']['bonuses'] = bonuses
        response['data']['bonus_message'] = f'Achieved {len(bonuses)} milestone(s)!'
    
    return jsonify(response), 200


@gamification_bp.route('/streak/status', methods=['GET'])
@jwt_required()
def streak_status():
    """
    Get the current streak status for the authenticated user.
    
    Returns:
        - streak_days: Current streak count
        - last_active: Timestamp of last activity
        - status: 'active_today', 'active_yesterday', or 'streak_broken'
        - hours_since_active: Hours since last activity
        - message: Human-readable status message
    """
    user_id = get_jwt_identity()
    
    status = get_streak_status(user_id)
    
    if status is None:
        return error_response('User not found', 404, 'USER_NOT_FOUND')
    
    return jsonify({
        'success': True,
        'data': status
    }), 200

