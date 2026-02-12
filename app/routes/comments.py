from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.comment import Comment
from app.models.user import User
from app.models.learning_path import LearningPath, Resource
from datetime import datetime, timedelta

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('', methods=['GET'])
def get_comments():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    learning_path_id = request.args.get('learning_path_id', type=int)
    resource_id = request.args.get('resource_id', type=int)

    if not learning_path_id and not resource_id:
        return jsonify({'error': 'learning_path_id or resource_id is required'}), 400

    query = Comment.query.filter_by(parent_id=None)

    if learning_path_id:
        query = query.filter_by(learning_path_id=learning_path_id)
    if resource_id:
        query = query.filter_by(resource_id=resource_id)

    pagination = query.order_by(Comment.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    comments = []
    for comment in pagination.items:
        comment_dict = comment.to_dict()
        # Fetch replies (1 level deep)
        replies = Comment.query.filter_by(parent_id=comment.id)\
            .order_by(Comment.created_at.asc()).all()
        comment_dict['replies'] = [reply.to_dict() for reply in replies]
        comments.append(comment_dict)

    return jsonify({
        'comments': comments,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@comments_bp.route('', methods=['POST'])
@jwt_required()
def create_comment():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    content = data.get('content')
    learning_path_id = data.get('learning_path_id')
    resource_id = data.get('resource_id')
    parent_id = data.get('parent_id')

    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    if not learning_path_id and not resource_id:
        return jsonify({'error': 'learning_path_id or resource_id is required'}), 400

    # Validate existence of target
    if learning_path_id:
        target = LearningPath.query.get(learning_path_id)
        if not target:
            return jsonify({'error': 'Learning path not found'}), 404
    elif resource_id:
        target = Resource.query.get(resource_id)
        if not target:
            return jsonify({'error': 'Resource not found'}), 404
            
    if parent_id:
        parent = Comment.query.get(parent_id)
        if not parent:
            return jsonify({'error': 'Parent comment not found'}), 404
        # Ensure we don't nest deeper than 1 level (parent must not have a parent)
        if parent.parent_id:
             # If parent is already a reply, set the new comment's parent to the top-level parent?
             # Or just Error? Requirement says "Nested replies (1 level deep)".
             # Usually means top level -> reply. Reply -> Reply is not allowed or flattened.
             # Let's flatten or restrict. Let's restrict for simplicity unless commonly flattened.
             # "Nested replies (1 level deep)" might mean: Comment -> Reply. (Depth 1).
             return jsonify({'error': 'Nested replies limited to 1 level'}), 400

    new_comment = Comment(
        content=content,
        user_id=current_user_id,
        learning_path_id=learning_path_id,
        resource_id=resource_id,
        parent_id=parent_id
    )

    db.session.add(new_comment)
    
    # Award XP +5
    user = User.query.get(current_user_id)
    if user:
        user.xp += 5
        # We might want to notify or log this, but direct modification is verified.

    db.session.commit()

    return jsonify(new_comment.to_dict()), 201

@comments_bp.route('/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    current_user_id = int(get_jwt_identity())
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if comment.is_deleted:
        return jsonify({'error': 'Cannot edit deleted comment'}), 400

    # Check 15 minute window
    if datetime.utcnow() - comment.created_at > timedelta(minutes=15):
        return jsonify({'error': 'Edit window has expired (15 minutes)'}), 403

    data = request.get_json()
    content = data.get('content')

    if not content:
        return jsonify({'error': 'Content is required'}), 400

    comment.content = content
    db.session.commit()

    return jsonify(comment.to_dict()), 200

@comments_bp.route('/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    current_user_id = int(get_jwt_identity())
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != current_user_id:
         # Optionally allow admins/moderators to delete
         # For now, only owner
         return jsonify({'error': 'Unauthorized'}), 403

    comment.is_deleted = True
    db.session.commit()

    return jsonify({'message': 'Comment deleted'}), 200
