from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.gamification import Badge, UserBadge, Challenge, Leaderboard, Achievement
from app.services.streak_service import update_user_streak, award_streak_bonus, get_streak_status
from app.services.leaderboard_service import get_leaderboard, get_user_rank, get_period_stats
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
    'period': {'type': str, 'allowed': ['daily', 'weekly', 'monthly', 'all_time'], 'default': 'all_time'},
    'limit': {'type': int, 'min': 1, 'max': 100, 'default': 50}
})
def get_leaderboard_endpoint():
    """
    Get the user leaderboard.
    
    Query Parameters:
        period (str): Time period filter (daily, weekly, monthly, all_time)
        limit (int): Number of entries to return (1-100, default: 50)
    
    Returns:
        - leaderboard: List of users ranked by XP
        - period: The period filter used
        - count: Number of entries returned
        - stats: Period statistics (optional)
    """
    try:
        period = request.args.get('period', 'all_time')
        limit = request.args.get('limit', 50, type=int)
        
        # Get leaderboard from service
        leaderboard = get_leaderboard(period=period, limit=limit)
        
        # Get period stats
        stats = get_period_stats(period)
        
        return jsonify({
            'success': True,
            'data': {
                'leaderboard': leaderboard,
                'period': period,
                'stats': stats
            },
            'count': len(leaderboard)
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        return error_response('Failed to fetch leaderboard', 500, 'LEADERBOARD_ERROR')


@gamification_bp.route('/leaderboard/me', methods=['GET'])
@jwt_required()
@validate_query_params({
    'period': {'type': str, 'allowed': ['daily', 'weekly', 'monthly', 'all_time'], 'default': 'all_time'}
})
def get_my_rank():
    """
    Get the current authenticated user's rank on the leaderboard.
    
    Query Parameters:
        period (str): Time period filter (daily, weekly, monthly, all_time)
    
    Returns:
        - user_rank: The user's current rank
        - user: User details (id, username, avatar_url, xp, points)
        - surrounding_users: List of users ranked before/after the current user
        - period: The period used for the query
        - total_users: Total number of users in the leaderboard
    """
    try:
        user_id = int(get_jwt_identity())
        period = request.args.get('period', 'all_time')
        
        # Get user rank from service
        rank_info = get_user_rank(user_id, period=period)
        
        return jsonify({
            'success': True,
            'data': rank_info
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching user rank: {e}")
        return error_response(str(e), 400, 'RANK_ERROR')


@gamification_bp.route('/leaderboard/<int:user_id>', methods=['GET'])
@validate_query_params({
    'period': {'type': str, 'allowed': ['daily', 'weekly', 'monthly', 'all_time'], 'default': 'all_time'}
})
def get_user_rank_endpoint(user_id):
    """
    Get a specific user's rank on the leaderboard.
    
    Args:
        user_id (int): The ID of the user
    
    Query Parameters:
        period (str): Time period filter (daily, weekly, monthly, all_time)
    
    Returns:
        - user_rank: The user's current rank
        - user: User details (id, username, avatar_url, xp, points)
        - surrounding_users: List of users ranked before/after the current user
        - period: The period used for the query
        - total_users: Total number of users in the leaderboard
    """
    try:
        # Validate user_id
        if user_id <= 0:
            return error_response('Invalid user ID', 400, 'INVALID_USER_ID')
        
        period = request.args.get('period', 'all_time')
        
        # Get user rank from service
        rank_info = get_user_rank(user_id, period=period)
        
        return jsonify({
            'success': True,
            'data': rank_info
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching user rank for user {user_id}: {e}")
        error_msg = str(e)
        if 'not found' in error_msg.lower():
            return error_response('User not found', 404, 'USER_NOT_FOUND')
        return error_response('Failed to fetch user rank', 500, 'RANK_ERROR')


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
    user_id = int(get_jwt_identity())
    
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

@gamification_bp.route('/badges/check', methods=['POST'])
@jwt_required()
@handle_db_errors
def check_and_award_badges():
    """
    Check user's activity and award any earned badges.
    Called after completing modules, quizzes, or other activities.
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return error_response('User not found', 404, 'USER_NOT_FOUND')

    from app.models.quiz import QuizAttempt
    from app.models.progress import UserProgress
    from app.models.comment import Comment

    awarded = []
    existing = {ub.badge_id for ub in UserBadge.query.filter_by(user_id=user_id).all()}

    # Helper: award badge by name if not already earned
    def try_award(badge_name):
        badge = Badge.query.filter_by(name=badge_name).first()
        if badge and badge.id not in existing:
            db.session.add(UserBadge(user_id=user_id, badge_id=badge.id))
            existing.add(badge.id)
            awarded.append(badge.to_dict())

    # 1. First Steps - completed at least 1 resource
    progress_records = UserProgress.query.filter_by(user_id=user_id).all()
    total_completed_resources = sum(len(p.get_completed_resources()) for p in progress_records)
    if total_completed_resources >= 1:
        try_award('First Steps')

    # 2. Path Finder - completed at least 1 learning path
    completed_paths = UserProgress.query.filter_by(user_id=user_id, status='completed').count()
    if completed_paths >= 1:
        try_award('Path Finder')

    # 3. Week Warrior - 7-day streak
    if user.streak_days >= 7:
        try_award('Week Warrior')

    # 4. Streak Legend - 30-day streak
    if user.streak_days >= 30:
        try_award('Streak Legend')

    # 5. Quiz Master - 5 perfect quizzes
    perfect_quizzes = QuizAttempt.query.filter_by(user_id=user_id).filter(QuizAttempt.score == 100).count()
    if perfect_quizzes >= 5:
        try_award('Quiz Master')

    # 6. Social Butterfly - 10 comments
    comment_count = Comment.query.filter_by(user_id=user_id).count()
    if comment_count >= 10:
        try_award('Social Butterfly')

    # 7. Code Ninja - 50 resources completed
    if total_completed_resources >= 50:
        try_award('Code Ninja')

    # 8. Mentor - contributor/admin with content
    if user.role in ('contributor', 'admin'):
        from app.models.learning_path import LearningPath
        created_paths = LearningPath.query.filter_by(creator_id=user_id).count()
        if created_paths >= 1:
            try_award('Mentor')

    if awarded:
        # Award XP for new badges
        xp_bonus = len(awarded) * 50
        user.xp += xp_bonus
        user.points += len(awarded) * 25
        db.session.commit()

    return jsonify({
        'success': True,
        'data': {
            'new_badges': awarded,
            'total_badges': len(existing),
            'xp_bonus': len(awarded) * 50 if awarded else 0
        }
    }), 200


@gamification_bp.route('/achievements/progress', methods=['GET'])
@jwt_required()
def get_achievements_progress():
    """Get user's progress toward each achievement."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return error_response('User not found', 404, 'USER_NOT_FOUND')

    from app.models.quiz import QuizAttempt
    from app.models.progress import UserProgress

    progress_records = UserProgress.query.filter_by(user_id=user_id).all()
    total_completed_resources = sum(len(p.get_completed_resources()) for p in progress_records)
    total_completed_modules = sum(len(p.get_completed_modules()) for p in progress_records)
    completed_paths = UserProgress.query.filter_by(user_id=user_id, status='completed').count()

    achievements = Achievement.query.all()
    result = []
    for a in achievements:
        current = 0
        if a.requirement_type == 'modules_completed':
            current = total_completed_modules
        elif a.requirement_type == 'paths_completed':
            current = completed_paths
        elif a.requirement_type == 'streak':
            current = user.streak_days
        elif a.requirement_type == 'resources_completed':
            current = total_completed_resources

        result.append({
            **a.to_dict(),
            'current': current,
            'target': a.requirement_value or 0,
            'unlocked': current >= (a.requirement_value or 0)
        })

    return jsonify({
        'success': True,
        'data': {'achievements': result},
        'count': len(result)
    }), 200


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
    user_id = int(get_jwt_identity())
    
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
    user_id = int(get_jwt_identity())
    
    status = get_streak_status(user_id)
    
    if status is None:
        return error_response('User not found', 404, 'USER_NOT_FOUND')
    
    return jsonify({
        'success': True,
        'data': status
    }), 200

