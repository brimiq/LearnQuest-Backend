from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.learning_path import LearningPath, Module, Resource
from app.models.user import User

learning_paths_bp = Blueprint('learning_paths', __name__)


@learning_paths_bp.route('/', methods=['GET'])
def get_learning_paths():
    paths = LearningPath.query.filter_by(is_published=True).all()
    return jsonify({'learning_paths': [path.to_dict() for path in paths]}), 200


@learning_paths_bp.route('/<int:path_id>', methods=['GET'])
def get_learning_path(path_id):
    path = LearningPath.query.get(path_id)
    if not path:
        return jsonify({'error': 'Learning path not found'}), 404
    
    path_data = path.to_dict()
    path_data['modules'] = [module.to_dict() for module in path.modules.order_by(Module.order).all()]
    
    return jsonify({'learning_path': path_data}), 200


@learning_paths_bp.route('/', methods=['POST'])
@jwt_required()
def create_learning_path():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role not in ['admin', 'contributor']:
        return jsonify({'error': 'Only contributors can create learning paths'}), 403
    
    data = request.get_json()
    
    path = LearningPath(
        title=data.get('title'),
        description=data.get('description'),
        category=data.get('category'),
        difficulty=data.get('difficulty'),
        image_url=data.get('image_url'),
        xp_reward=data.get('xp_reward', 100),
        creator_id=user_id
    )
    
    db.session.add(path)
    db.session.commit()
    
    return jsonify({
        'message': 'Learning path created!',
        'learning_path': path.to_dict()
    }), 201


@learning_paths_bp.route('/<int:path_id>/modules', methods=['POST'])
@jwt_required()
def add_module(path_id):
    user_id = get_jwt_identity()
    path = LearningPath.query.get(path_id)
    
    if not path:
        return jsonify({'error': 'Learning path not found'}), 404
    
    if path.creator_id != user_id:
        return jsonify({'error': 'Not authorized to modify this path'}), 403
    
    data = request.get_json()
    
    module = Module(
        title=data.get('title'),
        description=data.get('description'),
        order=data.get('order', 0),
        xp_reward=data.get('xp_reward', 50),
        learning_path_id=path_id
    )
    
    db.session.add(module)
    db.session.commit()
    
    return jsonify({
        'message': 'Module added!',
        'module': module.to_dict()
    }), 201


@learning_paths_bp.route('/modules/<int:module_id>/resources', methods=['POST'])
@jwt_required()
def add_resource(module_id):
    module = Module.query.get(module_id)
    
    if not module:
        return jsonify({'error': 'Module not found'}), 404
    
    data = request.get_json()
    
    resource = Resource(
        title=data.get('title'),
        description=data.get('description'),
        resource_type=data.get('resource_type'),
        url=data.get('url'),
        content=data.get('content'),
        order=data.get('order', 0),
        module_id=module_id
    )
    
    db.session.add(resource)
    db.session.commit()
    
    return jsonify({
        'message': 'Resource added!',
        'resource': resource.to_dict()
    }), 201


@learning_paths_bp.route('/<int:path_id>/rate', methods=['POST'])
@jwt_required()
def rate_path(path_id):
    path = LearningPath.query.get(path_id)
    
    if not path:
        return jsonify({'error': 'Learning path not found'}), 404
    
    data = request.get_json()
    rating = data.get('rating', 0)
    
    if not 1 <= rating <= 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    # Update average rating
    total = path.rating * path.total_ratings + rating
    path.total_ratings += 1
    path.rating = total / path.total_ratings
    
    db.session.commit()
    
    return jsonify({
        'message': 'Rating submitted!',
        'new_rating': path.rating
    }), 200
