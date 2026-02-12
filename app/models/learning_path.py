from app import db
from datetime import datetime


class LearningPath(db.Model):
    __tablename__ = 'learning_paths'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    difficulty = db.Column(db.String(50))  # beginner, intermediate, advanced
    image_url = db.Column(db.String(256))
    xp_reward = db.Column(db.Integer, default=100)
    
    # Creator relationship
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Status
    is_published = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    
    # Stats
    rating = db.Column(db.Float, default=0.0)
    total_ratings = db.Column(db.Integer, default=0)
    enrolled_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    modules = db.relationship('Module', backref='learning_path', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'difficulty': self.difficulty,
            'image_url': self.image_url,
            'xp_reward': self.xp_reward,
            'creator_id': self.creator_id,
            'is_published': self.is_published,
            'is_approved': self.is_approved,
            'rating': self.rating,
            'enrolled_count': self.enrolled_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Module(db.Model):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    xp_reward = db.Column(db.Integer, default=50)
    
    # Parent learning path
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    resources = db.relationship('Resource', backref='module', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'order': self.order,
            'xp_reward': self.xp_reward,
            'learning_path_id': self.learning_path_id
        }


class Resource(db.Model):
    __tablename__ = 'resources'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    resource_type = db.Column(db.String(50))  # video, article, tutorial, quiz
    url = db.Column(db.String(512))
    content = db.Column(db.Text)  # For quizzes or embedded content
    order = db.Column(db.Integer, default=0)
    
    # Parent module
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    
    # Stats
    rating = db.Column(db.Float, default=0.0)
    total_ratings = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'resource_type': self.resource_type,
            'url': self.url,
            'order': self.order,
            'rating': self.rating,
            'module_id': self.module_id
        }
