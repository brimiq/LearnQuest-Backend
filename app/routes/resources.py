from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.learning_path import Resource

resources_bp = Blueprint('resources', __name__)


@resources_bp.route('/', methods=['GET'])
def get_resources():
    resource_type = request.args.get('type')
    
    query = Resource.query
    if resource_type:
        query = query.filter_by(resource_type=resource_type)
    
    resources = query.all()
    return jsonify({'resources': [r.to_dict() for r in resources]}), 200


@resources_bp.route('/<int:resource_id>', methods=['GET'])
def get_resource(resource_id):
    resource = Resource.query.get(resource_id)
    if not resource:
        return jsonify({'error': 'Resource not found'}), 404
    return jsonify({'resource': resource.to_dict()}), 200


@resources_bp.route('/<int:resource_id>/rate', methods=['POST'])
@jwt_required()
def rate_resource(resource_id):
    resource = Resource.query.get(resource_id)
    
    if not resource:
        return jsonify({'error': 'Resource not found'}), 404
    
    data = request.get_json()
    rating = data.get('rating', 0)
    
    if not 1 <= rating <= 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    # Update average rating
    total = resource.rating * resource.total_ratings + rating
    resource.total_ratings += 1
    resource.rating = total / resource.total_ratings
    
    db.session.commit()
    
    return jsonify({
        'message': 'Rating submitted!',
        'new_rating': resource.rating
    }), 200
