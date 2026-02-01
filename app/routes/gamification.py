from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.gamification import Badge, UserBadge, Challenge, Leaderboard, Achievement

gamification_bp = Blueprint('gamification', __name__)


@gamification_bp.route('/badges', methods=['GET'])
def get_badges():
    badges = Badge.query.all()
    return jsonify({'badges': [badge.to_dict() for badge in badges]}), 200


@gamification_bp.route('/badges/<int:user_id>', methods=['GET'])
def get_user_badges(user_id):
    user_badges = UserBadge.query.filter_by(user_id=user_id).all()
    return jsonify({'badges': [ub.to_dict() for ub in user_badges]}), 200


@gamification_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    period = request.args.get('period', 'all_time')
    limit = request.args.get('limit', 10, type=int)
    
    # Get top users by XP
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
    
    return jsonify({'leaderboard': leaderboard, 'period': period}), 200


@gamification_bp.route('/challenges', methods=['GET'])
def get_challenges():
    active_only = request.args.get('active', 'true').lower() == 'true'
    
    query = Challenge.query
    if active_only:
        query = query.filter_by(is_active=True)
    
    challenges = query.all()
    return jsonify({'challenges': [c.to_dict() for c in challenges]}), 200


@gamification_bp.route('/challenges/<int:challenge_id>', methods=['GET'])
def get_challenge(challenge_id):
    challenge = Challenge.query.get(challenge_id)
    if not challenge:
        return jsonify({'error': 'Challenge not found'}), 404
    return jsonify({'challenge': challenge.to_dict()}), 200


@gamification_bp.route('/achievements', methods=['GET'])
def get_achievements():
    achievements = Achievement.query.all()
    return jsonify({'achievements': [a.to_dict() for a in achievements]}), 200


@gamification_bp.route('/xp/add', methods=['POST'])
@jwt_required()
def add_xp():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    xp_amount = data.get('xp', 0)
    
    user.xp += xp_amount
    db.session.commit()
    
    return jsonify({
        'message': f'Added {xp_amount} XP!',
        'total_xp': user.xp
    }), 200
