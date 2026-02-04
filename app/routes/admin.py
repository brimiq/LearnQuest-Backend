"""
Admin routes for LearnQuest.
Provides endpoints for dashboard stats, content approval, user management, and moderation.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, or_

from app import db
from app.models.user import User
from app.models.learning_path import LearningPath
from app.models.comment import Comment
from app.models.report import Report, Notification
from app.utils.decorators import admin_required, error_response, handle_db_errors

admin_bp = Blueprint('admin', __name__)


# ============================================================================
# Dashboard Statistics
# ============================================================================

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_dashboard_stats():
    """
    Get dashboard statistics for admin overview.
    
    Returns:
        JSON with total users, learning paths, active learners, pending approvals
    """
    # Date calculations
    today = datetime.utcnow().date()
    last_week = datetime.utcnow() - timedelta(days=7)
    two_weeks_ago = datetime.utcnow() - timedelta(days=14)
    
    # Total users with growth
    total_users = User.query.count()
    users_last_week = User.query.filter(User.created_at >= last_week).count()
    users_prev_week = User.query.filter(
        User.created_at >= two_weeks_ago,
        User.created_at < last_week
    ).count()
    
    user_growth = 0
    if users_prev_week > 0:
        user_growth = round(((users_last_week - users_prev_week) / users_prev_week) * 100, 1)
    elif users_last_week > 0:
        user_growth = 100.0
    
    # Learning paths stats
    total_paths = LearningPath.query.filter_by(is_published=True).count()
    
    # Active learners today (users active today)
    active_today = User.query.filter(
        func.date(User.last_active) == today
    ).count()
    
    # Pending approvals
    pending_approvals = LearningPath.query.filter_by(
        is_published=True,
        is_approved=False
    ).count()
    
    # Pending moderation reports
    pending_reports = Report.query.filter_by(status='pending').count()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_users': total_users,
            'user_growth_percent': user_growth,
            'total_learning_paths': total_paths,
            'active_learners_today': active_today,
            'pending_approvals': pending_approvals,
            'pending_reports': pending_reports
        }
    }), 200


# ============================================================================
# Pending Learning Path Approvals
# ============================================================================

@admin_bp.route('/pending', methods=['GET'])
@jwt_required()
@admin_required
def get_pending_paths():
    """
    Get list of learning paths pending approval.
    
    Returns:
        JSON with list of pending learning paths
    """
    pending = LearningPath.query.filter_by(
        is_published=True,
        is_approved=False
    ).order_by(LearningPath.created_at.desc()).all()
    
    result = []
    for path in pending:
        path_dict = path.to_dict()
        path_dict['creator'] = {
            'id': path.creator.id,
            'username': path.creator.username,
            'email': path.creator.email
        }
        path_dict['modules_count'] = path.modules.count()
        result.append(path_dict)
    
    return jsonify({
        'success': True,
        'pending_paths': result,
        'total': len(result)
    }), 200


@admin_bp.route('/approve/<int:path_id>', methods=['POST'])
@jwt_required()
@admin_required
@handle_db_errors
def approve_path(path_id):
    """
    Approve a learning path.
    Awards XP to creator and sends notification.
    """
    path = LearningPath.query.get(path_id)
    
    if not path:
        return error_response('Learning path not found', 404, 'PATH_NOT_FOUND')
    
    if path.is_approved:
        return error_response('Path is already approved', 400, 'ALREADY_APPROVED')
    
    # Approve the path
    path.is_approved = True
    
    # Award XP to creator (100 XP for approved path)
    xp_reward = 100
    path.creator.xp += xp_reward
    
    # Create notification for creator
    notification = Notification(
        user_id=path.creator_id,
        type='path_approved',
        title='Learning Path Approved! 🎉',
        message=f'Your learning path "{path.title}" has been approved and is now live!',
        related_type='learning_path',
        related_id=path.id
    )
    db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Learning path "{path.title}" approved successfully',
        'xp_awarded': xp_reward
    }), 200


@admin_bp.route('/reject/<int:path_id>', methods=['POST'])
@jwt_required()
@admin_required
@handle_db_errors
def reject_path(path_id):
    """
    Reject a learning path with a reason.
    Request body should contain 'reason' field.
    """
    path = LearningPath.query.get(path_id)
    
    if not path:
        return error_response('Learning path not found', 404, 'PATH_NOT_FOUND')
    
    data = request.get_json() or {}
    reason = data.get('reason', 'No reason provided')
    
    # Unpublish the path (keep it as draft)
    path.is_published = False
    path.is_approved = False
    
    # Create notification for creator
    notification = Notification(
        user_id=path.creator_id,
        type='path_rejected',
        title='Learning Path Needs Revision',
        message=f'Your learning path "{path.title}" was not approved. Reason: {reason}',
        related_type='learning_path',
        related_id=path.id
    )
    db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Learning path "{path.title}" rejected',
        'reason': reason
    }), 200


# ============================================================================
# User Management
# ============================================================================

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    """
    Get list of users with optional filters.
    
    Query params:
        - search: Search by username or email
        - role: Filter by role (admin, contributor, learner)
        - status: Filter by status (active, suspended, banned)
        - page: Page number (default 1)
        - per_page: Items per page (default 20)
    """
    search = request.args.get('search', '')
    role = request.args.get('role', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = User.query
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )
    
    if role:
        query = query.filter_by(role=role)
    
    if status:
        query = query.filter_by(status=status)
    
    # Paginate
    query = query.order_by(User.created_at.desc())
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    users = []
    for user in paginated.items:
        user_dict = user.to_dict()
        user_dict['status'] = getattr(user, 'status', 'active')
        users.append(user_dict)
    
    return jsonify({
        'success': True,
        'users': users,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': paginated.total,
            'pages': paginated.pages
        }
    }), 200


@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@jwt_required()
@admin_required
@handle_db_errors
def change_user_role(user_id):
    """
    Change a user's role.
    Request body should contain 'role' field.
    """
    user = User.query.get(user_id)
    
    if not user:
        return error_response('User not found', 404, 'USER_NOT_FOUND')
    
    data = request.get_json()
    if not data or 'role' not in data:
        return error_response('Role is required', 400, 'MISSING_ROLE')
    
    new_role = data['role']
    valid_roles = ['admin', 'contributor', 'learner']
    
    if new_role not in valid_roles:
        return error_response(
            f'Invalid role. Must be one of: {", ".join(valid_roles)}',
            400,
            'INVALID_ROLE'
        )
    
    old_role = user.role
    user.role = new_role
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'User role changed from {old_role} to {new_role}',
        'user': user.to_dict()
    }), 200


@admin_bp.route('/users/<int:user_id>/suspend', methods=['PUT'])
@jwt_required()
@admin_required
@handle_db_errors
def suspend_user(user_id):
    """
    Suspend or unsuspend a user.
    Request body can contain 'suspend' (boolean, default true).
    """
    admin_id = get_jwt_identity()
    
    if user_id == admin_id:
        return error_response('Cannot suspend yourself', 400, 'SELF_SUSPEND')
    
    user = User.query.get(user_id)
    
    if not user:
        return error_response('User not found', 404, 'USER_NOT_FOUND')
    
    data = request.get_json() or {}
    should_suspend = data.get('suspend', True)
    
    user.status = 'suspended' if should_suspend else 'active'
    db.session.commit()
    
    action = 'suspended' if should_suspend else 'reactivated'
    
    return jsonify({
        'success': True,
        'message': f'User {action} successfully',
        'user': user.to_dict()
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
@handle_db_errors
def delete_user(user_id):
    """
    Delete a user account.
    """
    admin_id = get_jwt_identity()
    
    if user_id == admin_id:
        return error_response('Cannot delete yourself', 400, 'SELF_DELETE')
    
    user = User.query.get(user_id)
    
    if not user:
        return error_response('User not found', 404, 'USER_NOT_FOUND')
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'User "{username}" deleted successfully'
    }), 200


# ============================================================================
# Content Moderation
# ============================================================================

@admin_bp.route('/reports', methods=['GET'])
@jwt_required()
@admin_required
def get_reports():
    """
    Get content moderation queue (reported items).
    
    Query params:
        - status: Filter by status (pending, dismissed, actioned)
        - content_type: Filter by content type (comment, resource)
    """
    status = request.args.get('status', 'pending')
    content_type = request.args.get('content_type', '')
    
    query = Report.query
    
    if status:
        query = query.filter_by(status=status)
    
    if content_type:
        query = query.filter_by(content_type=content_type)
    
    reports = query.order_by(Report.created_at.desc()).all()
    
    result = []
    for report in reports:
        report_dict = report.to_dict()
        
        # Add content preview
        if report.content_type == 'comment':
            comment = Comment.query.get(report.content_id)
            if comment:
                report_dict['content_preview'] = {
                    'content': comment.content[:200] if comment.content else '',
                    'author': comment.user.username if comment.user else 'Unknown'
                }
        
        result.append(report_dict)
    
    return jsonify({
        'success': True,
        'reports': result,
        'total': len(result)
    }), 200


@admin_bp.route('/reports/<int:report_id>/dismiss', methods=['POST'])
@jwt_required()
@admin_required
@handle_db_errors
def dismiss_report(report_id):
    """
    Dismiss a report (no action needed).
    """
    admin_id = get_jwt_identity()
    report = Report.query.get(report_id)
    
    if not report:
        return error_response('Report not found', 404, 'REPORT_NOT_FOUND')
    
    report.status = 'dismissed'
    report.resolved_at = datetime.utcnow()
    report.resolved_by = admin_id
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Report dismissed'
    }), 200


@admin_bp.route('/reports/<int:report_id>/action', methods=['POST'])
@jwt_required()
@admin_required
@handle_db_errors
def action_report(report_id):
    """
    Take action on a report.
    
    Request body:
        - action: 'warn', 'remove', or 'ban'
        - notes: Optional admin notes
    """
    admin_id = get_jwt_identity()
    report = Report.query.get(report_id)
    
    if not report:
        return error_response('Report not found', 404, 'REPORT_NOT_FOUND')
    
    data = request.get_json() or {}
    action = data.get('action')
    notes = data.get('notes', '')
    
    valid_actions = ['warn', 'remove', 'ban']
    if action not in valid_actions:
        return error_response(
            f'Invalid action. Must be one of: {", ".join(valid_actions)}',
            400,
            'INVALID_ACTION'
        )
    
    # Process the action
    if report.content_type == 'comment':
        comment = Comment.query.get(report.content_id)
        if comment:
            if action == 'remove':
                comment.is_deleted = True
            elif action == 'warn':
                # Send warning notification to comment author
                notification = Notification(
                    user_id=comment.user_id,
                    type='content_warning',
                    title='Content Warning',
                    message='Your comment was flagged for review. Please follow community guidelines.',
                    related_type='comment',
                    related_id=comment.id
                )
                db.session.add(notification)
            elif action == 'ban':
                if comment.user:
                    comment.user.status = 'banned'
                comment.is_deleted = True
    
    # Update report
    report.status = 'actioned'
    report.action_taken = action
    report.admin_notes = notes
    report.resolved_at = datetime.utcnow()
    report.resolved_by = admin_id
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Action "{action}" taken successfully',
        'report': report.to_dict()
    }), 200
