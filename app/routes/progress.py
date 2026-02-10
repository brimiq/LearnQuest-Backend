from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.learning_path import LearningPath, Module, Resource
from app.models.progress import UserProgress, ResourceCompletion
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

progress_bp = Blueprint('progress', __name__)


@progress_bp.route('/enroll/<int:path_id>', methods=['POST'])
@jwt_required()
def enroll_in_path(path_id):
    """Enroll user in a learning path."""
    user_id = get_jwt_identity()
    
    path = LearningPath.query.get(path_id)
    if not path:
        return jsonify({'error': 'Learning path not found'}), 404
    
    # Check if already enrolled
    existing = UserProgress.query.filter_by(
        user_id=user_id,
        learning_path_id=path_id
    ).first()
    
    if existing:
        return jsonify({
            'success': True,
            'message': 'Already enrolled',
            'data': {'progress': existing.to_dict()}
        }), 200
    
    # Create new enrollment
    progress = UserProgress(
        user_id=user_id,
        learning_path_id=path_id,
        status='in_progress'
    )
    
    # Set first module as current
    first_module = Module.query.filter_by(
        learning_path_id=path_id
    ).order_by(Module.order).first()
    if first_module:
        progress.current_module_id = first_module.id
    
    # Increment enrolled count
    path.enrolled_count += 1
    
    db.session.add(progress)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Successfully enrolled!',
        'data': {'progress': progress.to_dict()}
    }), 201


@progress_bp.route('/my-paths', methods=['GET'])
@jwt_required()
def get_my_paths():
    """Get all learning paths the user is enrolled in."""
    user_id = get_jwt_identity()
    
    progress_entries = UserProgress.query.filter_by(
        user_id=user_id
    ).order_by(UserProgress.last_accessed.desc()).all()
    
    result = []
    for p in progress_entries:
        path_data = p.learning_path.to_dict() if p.learning_path else {}
        path_data['progress'] = p.to_dict()
        result.append(path_data)
    
    return jsonify({
        'success': True,
        'data': {'paths': result},
        'count': len(result)
    }), 200


@progress_bp.route('/path/<int:path_id>', methods=['GET'])
@jwt_required()
def get_path_progress(path_id):
    """Get user's progress for a specific learning path."""
    user_id = get_jwt_identity()
    
    progress = UserProgress.query.filter_by(
        user_id=user_id,
        learning_path_id=path_id
    ).first()
    
    if not progress:
        return jsonify({
            'success': True,
            'data': {'enrolled': False, 'progress': None}
        }), 200
    
    return jsonify({
        'success': True,
        'data': {'enrolled': True, 'progress': progress.to_dict()}
    }), 200


@progress_bp.route('/complete-resource/<int:resource_id>', methods=['POST'])
@jwt_required()
def complete_resource(resource_id):
    """Mark a resource as completed."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    resource = Resource.query.get(resource_id)
    if not resource:
        return jsonify({'error': 'Resource not found'}), 404
    
    # Check if already completed
    existing = ResourceCompletion.query.filter_by(
        user_id=user_id,
        resource_id=resource_id
    ).first()
    
    if existing:
        return jsonify({
            'success': True,
            'message': 'Resource already completed',
            'data': {'completion': existing.to_dict()}
        }), 200
    
    data = request.get_json() or {}
    time_spent = data.get('time_spent', 0)
    
    # Award XP for completion
    xp_earned = 10  # Base XP for completing a resource
    
    completion = ResourceCompletion(
        user_id=user_id,
        resource_id=resource_id,
        time_spent=time_spent,
        xp_earned=xp_earned
    )
    
    # Update user XP
    user.xp += xp_earned
    
    # Update user progress for the learning path
    module = resource.module
    if module:
        progress = UserProgress.query.filter_by(
            user_id=user_id,
            learning_path_id=module.learning_path_id
        ).first()
        
        if progress:
            progress.add_completed_resource(resource_id)
            progress.last_accessed = datetime.utcnow()
            progress.xp_earned += xp_earned
            progress.time_spent += time_spent // 60  # Convert to minutes
            
            # Calculate new progress percentage
            path = progress.learning_path
            if path:
                total_resources = sum(m.resources.count() for m in path.modules.all())
                if total_resources > 0:
                    completed_count = len(progress.get_completed_resources())
                    progress.progress_percentage = (completed_count / total_resources) * 100
    
    db.session.add(completion)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Resource completed! +{xp_earned} XP',
        'data': {
            'completion': completion.to_dict(),
            'xp_earned': xp_earned,
            'total_xp': user.xp
        }
    }), 201


@progress_bp.route('/complete-module/<int:module_id>', methods=['POST'])
@jwt_required()
def complete_module(module_id):
    """Mark a module as completed."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    module = Module.query.get(module_id)
    if not module:
        return jsonify({'error': 'Module not found'}), 404
    
    progress = UserProgress.query.filter_by(
        user_id=user_id,
        learning_path_id=module.learning_path_id
    ).first()
    
    if not progress:
        return jsonify({'error': 'Not enrolled in this learning path'}), 400
    
    # Check if already completed
    if module_id in progress.get_completed_modules():
        return jsonify({
            'success': True,
            'message': 'Module already completed'
        }), 200
    
    # Mark module as completed
    progress.add_completed_module(module_id)
    progress.last_accessed = datetime.utcnow()
    
    # Award XP
    xp_earned = module.xp_reward
    user.xp += xp_earned
    progress.xp_earned += xp_earned
    
    # Set next module as current
    next_module = Module.query.filter(
        Module.learning_path_id == module.learning_path_id,
        Module.order > module.order
    ).order_by(Module.order).first()
    
    if next_module:
        progress.current_module_id = next_module.id
    else:
        # All modules completed
        progress.status = 'completed'
        progress.completed_at = datetime.utcnow()
        progress.progress_percentage = 100
        
        # Bonus XP for completing the path
        path_bonus = progress.learning_path.xp_reward if progress.learning_path else 100
        user.xp += path_bonus
        xp_earned += path_bonus
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Module completed! +{xp_earned} XP',
        'data': {
            'xp_earned': xp_earned,
            'total_xp': user.xp,
            'progress': progress.to_dict()
        }
    }), 200
