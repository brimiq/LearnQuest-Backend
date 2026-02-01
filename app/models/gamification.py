from app import db
from datetime import datetime


class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon_url = db.Column(db.String(256))
    xp_reward = db.Column(db.Integer, default=0)
    points_reward = db.Column(db.Integer, default=0)
    requirement_type = db.Column(db.String(50))  # modules_completed, paths_completed, streak, etc.
    requirement_value = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon_url': self.icon_url,
            'xp_reward': self.xp_reward,
            'points_reward': self.points_reward
        }


class Badge(db.Model):
    __tablename__ = 'badges'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon_url = db.Column(db.String(256))
    badge_type = db.Column(db.String(50))  # bronze, silver, gold, platinum, special
    is_seasonal = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon_url': self.icon_url,
            'badge_type': self.badge_type,
            'is_seasonal': self.is_seasonal
        }


class UserBadge(db.Model):
    __tablename__ = 'user_badges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    badge = db.relationship('Badge', backref='user_badges')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'badge': self.badge.to_dict() if self.badge else None,
            'earned_at': self.earned_at.isoformat() if self.earned_at else None
        }


class Challenge(db.Model):
    __tablename__ = 'challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    challenge_type = db.Column(db.String(50))  # weekly, monthly, seasonal
    xp_reward = db.Column(db.Integer, default=0)
    points_reward = db.Column(db.Integer, default=0)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'))
    
    # Challenge requirements
    requirement_type = db.Column(db.String(50))
    requirement_value = db.Column(db.Integer)
    
    # Duration
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    badge = db.relationship('Badge', backref='challenges')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'challenge_type': self.challenge_type,
            'xp_reward': self.xp_reward,
            'points_reward': self.points_reward,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active
        }


class Leaderboard(db.Model):
    __tablename__ = 'leaderboard'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    period_type = db.Column(db.String(20))  # daily, weekly, monthly, all_time
    period_start = db.Column(db.DateTime)
    points = db.Column(db.Integer, default=0)
    rank = db.Column(db.Integer)
    
    user = db.relationship('User', backref='leaderboard_entries')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'period_type': self.period_type,
            'points': self.points,
            'rank': self.rank
        }
