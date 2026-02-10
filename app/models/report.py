"""
Report model for content moderation in LearnQuest.
Tracks reported comments and resources for admin review.
"""
from app import db
from datetime import datetime


class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Reporter info
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # What is being reported
    content_type = db.Column(db.String(20), nullable=False)  # 'comment' or 'resource'
    content_id = db.Column(db.Integer, nullable=False)
    
    # Report details
    reason = db.Column(db.String(100), nullable=False)  # spam, harassment, inappropriate, etc.
    details = db.Column(db.Text)  # Additional details from reporter
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, dismissed, actioned
    action_taken = db.Column(db.String(50))  # warn, remove, ban
    admin_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='reports_filed')
    resolver = db.relationship('User', foreign_keys=[resolved_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'reporter_id': self.reporter_id,
            'reporter': {
                'id': self.reporter.id,
                'username': self.reporter.username
            } if self.reporter else None,
            'content_type': self.content_type,
            'content_id': self.content_id,
            'reason': self.reason,
            'details': self.details,
            'status': self.status,
            'action_taken': self.action_taken,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Notification content
    type = db.Column(db.String(50), nullable=False)  # path_approved, path_rejected, xp_earned, etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    
    # Related entity (optional)
    related_type = db.Column(db.String(50))  # learning_path, badge, etc.
    related_id = db.Column(db.Integer)
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='notifications')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'related_type': self.related_type,
            'related_id': self.related_id,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
