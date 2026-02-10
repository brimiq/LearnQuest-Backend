from app import db
from datetime import datetime


class UserProgress(db.Model):
    __tablename__ = 'user_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=False)
    
    # Progress tracking
    current_module_id = db.Column(db.Integer, db.ForeignKey('modules.id'))
    completed_modules = db.Column(db.Text, default='[]')  # JSON array of module IDs
    completed_resources = db.Column(db.Text, default='[]')  # JSON array of resource IDs
    
    # Stats
    progress_percentage = db.Column(db.Float, default=0.0)
    xp_earned = db.Column(db.Integer, default=0)
    time_spent = db.Column(db.Integer, default=0)  # Minutes
    
    # Status
    status = db.Column(db.String(20), default='in_progress')  # not_started, in_progress, completed
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='progress_entries')
    learning_path = db.relationship('LearningPath', backref='enrollments')
    current_module = db.relationship('Module')
    
    def get_completed_modules(self):
        import json
        if self.completed_modules:
            return json.loads(self.completed_modules)
        return []
    
    def add_completed_module(self, module_id):
        import json
        modules = self.get_completed_modules()
        if module_id not in modules:
            modules.append(module_id)
            self.completed_modules = json.dumps(modules)
    
    def get_completed_resources(self):
        import json
        if self.completed_resources:
            return json.loads(self.completed_resources)
        return []
    
    def add_completed_resource(self, resource_id):
        import json
        resources = self.get_completed_resources()
        if resource_id not in resources:
            resources.append(resource_id)
            self.completed_resources = json.dumps(resources)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'learning_path_id': self.learning_path_id,
            'learning_path_title': self.learning_path.title if self.learning_path else None,
            'current_module_id': self.current_module_id,
            'completed_modules': self.get_completed_modules(),
            'completed_resources': self.get_completed_resources(),
            'progress_percentage': self.progress_percentage,
            'xp_earned': self.xp_earned,
            'time_spent': self.time_spent,
            'status': self.status,
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class ResourceCompletion(db.Model):
    __tablename__ = 'resource_completions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    time_spent = db.Column(db.Integer, default=0)  # Seconds
    xp_earned = db.Column(db.Integer, default=0)
    
    user = db.relationship('User', backref='resource_completions')
    resource = db.relationship('Resource', backref='completions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'time_spent': self.time_spent,
            'xp_earned': self.xp_earned
        }
