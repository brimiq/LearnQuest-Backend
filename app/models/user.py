from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='learner')  # admin, contributor, learner
    status = db.Column(db.String(20), default='active')  # active, suspended, banned
    
    # Gamification fields
    xp = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)
    streak_days = db.Column(db.Integer, default=0)
    hours_learned = db.Column(db.Float, default=0.0)
    
    # Profile fields
    avatar_url = db.Column(db.String(256))
    bio = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    badges = db.relationship('UserBadge', backref='user', lazy='dynamic')
    learning_paths = db.relationship('LearningPath', backref='creator', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'status': self.status,
            'xp': self.xp,
            'points': self.points,
            'streak_days': self.streak_days,
            'hours_learned': self.hours_learned,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
