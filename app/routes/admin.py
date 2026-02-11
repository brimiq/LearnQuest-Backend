from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.learning_path import LearningPath, Module, Resource
from app.models.gamification import Challenge, Badge
from app.models.report import Report
from functools import wraps
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)


def admin_required(fn):
    """Decorator that checks if the current user is an admin."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper


@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_stats():
    """Get platform-wide statistics for admin dashboard."""
    total_users = User.query.count()
    total_learners = User.query.filter_by(role='learner').count()
    total_contributors = User.query.filter_by(role='contributor').count()
    total_paths = LearningPath.query.count()
    published_paths = LearningPath.query.filter_by(is_published=True, is_approved=True).count()
    pending_paths = LearningPath.query.filter_by(is_published=True, is_approved=False).count()
    total_resources = Resource.query.count()
    active_challenges = Challenge.query.filter_by(is_active=True).count()

    # Users joined this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_week = User.query.filter(User.created_at >= week_ago).count()

    return jsonify({
        'success': True,
        'data': {
            'total_users': total_users,
            'total_learners': total_learners,
            'total_contributors': total_contributors,
            'total_paths': total_paths,
            'published_paths': published_paths,
            'pending_approvals': pending_paths,
            'total_resources': total_resources,
            'active_challenges': active_challenges,
            'new_users_this_week': new_users_week
        }
    }), 200


@admin_bp.route('/pending', methods=['GET'])
@admin_required
def get_pending_paths():
    """Get learning paths pending approval."""
    paths = LearningPath.query.filter_by(
        is_published=True, is_approved=False
    ).order_by(LearningPath.created_at.desc()).all()

    result = []
    for path in paths:
        data = path.to_dict()
        creator = User.query.get(path.creator_id)
        data['creator_name'] = creator.username if creator else 'Unknown'
        data['creator_email'] = creator.email if creator else ''
        result.append(data)

    return jsonify({
        'success': True,
        'data': {'paths': result},
        'count': len(result)
    }), 200


@admin_bp.route('/approve/<int:path_id>', methods=['POST'])
@admin_required
def approve_path(path_id):
    """Approve a learning path."""
    path = LearningPath.query.get(path_id)
    if not path:
        return jsonify({'error': 'Learning path not found'}), 404

    path.is_approved = True
    
    # Award XP to creator
    creator = User.query.get(path.creator_id)
    if creator:
        creator.xp += 100
        creator.points += 50

    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Learning path "{path.title}" approved!',
        'data': {'path': path.to_dict()}
    }), 200


@admin_bp.route('/reject/<int:path_id>', methods=['POST'])
@admin_required
def reject_path(path_id):
    """Reject a learning path with a reason."""
    path = LearningPath.query.get(path_id)
    if not path:
        return jsonify({'error': 'Learning path not found'}), 404

    data = request.get_json() or {}
    reason = data.get('reason', 'Does not meet quality standards')

    path.is_published = False
    path.is_approved = False
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Learning path "{path.title}" rejected.',
        'data': {'reason': reason}
    }), 200


@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users with optional role filter."""
    role = request.args.get('role')
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = User.query
    if role:
        query = query.filter_by(role=role)
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'success': True,
        'data': {
            'users': [u.to_dict() for u in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }
    }), 200


@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@admin_required
def change_user_role(user_id):
    """Change a user's role."""
    admin_id = get_jwt_identity()
    if admin_id == user_id:
        return jsonify({'error': 'Cannot change your own role'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    new_role = data.get('role')

    if new_role not in ['learner', 'contributor', 'admin']:
        return jsonify({'error': 'Invalid role. Must be learner, contributor, or admin'}), 400

    user.role = new_role
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'User {user.username} role changed to {new_role}',
        'data': {'user': user.to_dict()}
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a user (soft-delete by deactivating)."""
    admin_id = get_jwt_identity()
    if admin_id == user_id:
        return jsonify({'error': 'Cannot delete yourself'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    username = user.username
    db.session.delete(user)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'User {username} deleted'
    }), 200


@admin_bp.route('/users/<int:user_id>/suspend', methods=['PUT'])
@admin_required
def suspend_user(user_id):
    """Suspend or reactivate a user."""
    admin_id = get_jwt_identity()
    if admin_id == user_id:
        return jsonify({'error': 'Cannot suspend yourself'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.status == 'suspended':
        user.status = 'active'
        message = f'User {user.username} reactivated'
    else:
        user.status = 'suspended'
        message = f'User {user.username} suspended'
    
    db.session.commit()
    return jsonify({'success': True, 'message': message, 'data': {'user': user.to_dict()}}), 200


@admin_bp.route('/reports', methods=['GET'])
@admin_required
def get_reports():
    """Get all reports for moderation."""
    status = request.args.get('status', 'pending')
    
    query = Report.query
    if status != 'all':
        query = query.filter_by(status=status)
    
    reports = query.order_by(Report.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'data': {'reports': [r.to_dict() for r in reports]},
        'count': len(reports)
    }), 200


@admin_bp.route('/reports/<int:report_id>/dismiss', methods=['POST'])
@admin_required
def dismiss_report(report_id):
    """Dismiss a report."""
    report = Report.query.get(report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    
    admin_id = get_jwt_identity()
    report.status = 'dismissed'
    report.resolved_at = datetime.utcnow()
    report.resolved_by = admin_id
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Report dismissed'}), 200


@admin_bp.route('/reports/<int:report_id>/action', methods=['POST'])
@admin_required
def action_report(report_id):
    """Take action on a report."""
    report = Report.query.get(report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    
    data = request.get_json() or {}
    action = data.get('action', 'warn')
    
    admin_id = get_jwt_identity()
    report.status = 'actioned'
    report.action_taken = action
    report.resolved_at = datetime.utcnow()
    report.resolved_by = admin_id
    report.admin_notes = data.get('notes', '')
    
    db.session.commit()
    return jsonify({'success': True, 'message': f'Report actioned: {action}'}), 200
