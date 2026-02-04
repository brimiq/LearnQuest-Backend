from app import db
from datetime import datetime

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'))
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))  # For replies
    
    # Timestamps & Soft Delete
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Relationships
    # Backref 'comments' adds a 'comments' attribute to the User model.
    # Note: If User model already defines 'comments' relationship (it didn't in my view), this matches.
    # Actually, User model did NOT define comments relationship in the file I viewed. 
    # But usually we define it on one side.
    
    user = db.relationship('User', backref='comments')
    
    # Self-referential relationship for replies
    replies = db.relationship(
        'Comment',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic',
        cascade='all, delete-orphan' # Consider if we want delete-orphan. Soft delete suggests maybe not, but physically if parent is gone?
        # Requirement says "Soft delete own comment". It implies we shouldn't delete from DB easily.
        # But if we did hard delete a comment, replies should probably go too or be handled.
        # Let's keep cascade standard for db integrity if hard delete happens.
    )

    def to_dict(self):
        """Convert comment to dictionary."""
        return {
            'id': self.id,
            'content': self.content if not self.is_deleted else '[This comment has been deleted]',
            'user_id': self.user_id,
            'learning_path_id': self.learning_path_id,
            'resource_id': self.resource_id,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_deleted': self.is_deleted,
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'avatar_url': self.user.avatar_url
            } if self.user else None
        }
