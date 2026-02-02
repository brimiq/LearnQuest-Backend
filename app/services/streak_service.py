"""
Streak Tracking Service for LearnQuest

Handles user streak logic, bonus XP awards, and badge unlocks
for consistent learning engagement.

With comprehensive error handling and logging.
"""

from datetime import datetime, timedelta
from app import db
from app.models.user import User
from app.models.gamification import Badge, UserBadge
import logging

logger = logging.getLogger(__name__)


class StreakError(Exception):
    """Custom exception for streak-related errors."""
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


def update_user_streak(user_id):
    """
    Update the user's learning streak based on their last active timestamp.
    
    Args:
        user_id (int): The ID of the user to update.
    
    Returns:
        dict: A dictionary containing the new streak count and streak status message.
              Returns None if user is not found.
    
    Raises:
        StreakError: If a database error occurs.
    
    Logic:
        - If user was active within the last 24 hours: no change (already counted today)
        - If user was active yesterday (24-48 hours ago): increment streak by 1
        - If user was inactive for more than 48 hours: reset streak to 1
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            logger.warning(f"User {user_id} not found for streak update")
            return None
        
        now = datetime.utcnow()
        
        # Initialize last_active if it's None
        if user.last_active is None:
            user.last_active = now
            user.streak_days = 1
            db.session.commit()
            logger.info(f"User {user_id} started streak. Initial streak: 1")
            return {
                'streak_days': user.streak_days,
                'message': 'Streak started! Welcome to LearnQuest!'
            }
        
        # Calculate time difference in hours
        hours_diff = (now - user.last_active).total_seconds() / 3600
        
        if hours_diff < 24:
            # Already active today, no streak change needed
            logger.debug(f"User {user_id} already active today. Streak: {user.streak_days}")
            return {
                'streak_days': user.streak_days,
                'message': 'Already counted for today. Keep up the momentum!'
            }
        
        elif 24 <= hours_diff < 48:
            # Active yesterday, increment streak
            user.streak_days += 1
            user.last_active = now
            db.session.commit()
            logger.info(f"User {user_id} streak incremented to {user.streak_days} days")
            return {
                'streak_days': user.streak_days,
                'message': f'Streak increased to {user.streak_days} days!'
            }
        
        else:
            # Missed more than one day, reset streak
            user.streak_days = 1
            user.last_active = now
            db.session.commit()
            logger.info(f"User {user_id} streak reset to 1 day")
            return {
                'streak_days': user.streak_days,
                'message': 'Streak reset. Start a new streak today!'
            }
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database error updating streak for user {user_id}: {e}")
        raise StreakError(f"Failed to update streak: {str(e)}", 'STREAK_UPDATE_ERROR')


def award_streak_bonus(user_id, streak_days):
    """
    Award XP bonuses and badges for reaching streak milestones.
    
    Args:
        user_id (int): The ID of the user.
        streak_days (int): The current streak day count.
    
    Returns:
        list: A list of dictionaries containing awarded bonuses and badges.
              Empty list if no bonuses were awarded.
    
    Raises:
        StreakError: If a database error occurs.
    """
    bonuses = []
    now = datetime.utcnow()
    
    try:
        # Define streak milestones
        milestones = [
            {'days': 7, 'xp': 50, 'badge_name': '7 Day Streak', 'badge_desc': 'Maintained a 7-day learning streak'},
            {'days': 30, 'xp': 200, 'badge_name': '30 Day Streak', 'badge_desc': 'Maintained a 30-day learning streak'},
            {'days': 100, 'xp': 500, 'badge_name': '100 Day Streak', 'badge_desc': 'Maintained a 100-day learning streak'},
        ]
        
        for milestone in milestones:
            if streak_days >= milestone['days']:
                # Check if badge already exists
                existing_badge = Badge.query.filter_by(name=milestone['badge_name']).first()
                
                if not existing_badge:
                    # Create the badge if it doesn't exist
                    existing_badge = Badge(
                        name=milestone['badge_name'],
                        description=milestone['badge_desc'],
                        icon_url=f'/static/badges/streak_{milestone["days"]}.png',
                        badge_type='streak'
                    )
                    db.session.add(existing_badge)
                    db.session.flush()  # Get the ID without committing
                
                # Check if user already has this badge
                has_badge = UserBadge.query.filter_by(
                    user_id=user_id,
                    badge_id=existing_badge.id
                ).first()
                
                if not has_badge:
                    # Award the badge
                    user_badge = UserBadge(
                        user_id=user_id,
                        badge_id=existing_badge.id,
                        earned_at=now
                    )
                    db.session.add(user_badge)
                    
                    # Award XP bonus
                    user = User.query.get(user_id)
                    if user:
                        user.xp += milestone['xp']
                        bonuses.append({
                            'type': 'milestone',
                            'days': milestone['days'],
                            'xp_awarded': milestone['xp'],
                            'badge': {
                                'id': existing_badge.id,
                                'name': existing_badge.name,
                                'description': existing_badge.description,
                                'icon_url': existing_badge.icon_url
                            }
                        })
                    else:
                        logger.warning(f"User {user_id} not found when awarding bonus")
        
        # Commit all changes
        if bonuses:
            db.session.commit()
            total_xp = sum(b['xp_awarded'] for b in bonuses)
            logger.info(f"Awarded {len(bonuses)} milestone(s) to user {user_id}. Total XP: {total_xp}")
        
        return bonuses
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database error awarding streak bonus to user {user_id}: {e}")
        raise StreakError(f"Failed to award streak bonus: {str(e)}", 'BONUS_AWARD_ERROR')


def get_streak_status(user_id):
    """
    Get the current streak status for a user without updating it.
    
    Args:
        user_id (int): The ID of the user.
    
    Returns:
        dict: A dictionary containing streak information.
              Returns None if user is not found.
    
    Raises:
        StreakError: If a database error occurs.
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            logger.debug(f"User {user_id} not found for streak status")
            return None
        
        now = datetime.utcnow()
        
        if user.last_active is None:
            return {
                'streak_days': 0,
                'last_active': None,
                'status': 'no_streak',
                'message': 'No activity recorded yet. Start learning today!'
            }
        
        hours_diff = (now - user.last_active).total_seconds() / 3600
        
        if hours_diff < 24:
            status = 'active_today'
            message = 'Keep going! Your streak is safe for today.'
        elif hours_diff < 48:
            status = 'active_yesterday'
            message = 'Active yesterday. Come back today to keep your streak!'
        else:
            status = 'streak_broken'
            message = 'Your streak has expired. Start a new one today!'
        
        return {
            'streak_days': user.streak_days,
            'last_active': user.last_active.isoformat() if user.last_active else None,
            'hours_since_active': round(hours_diff, 2),
            'status': status,
            'message': message
        }
    
    except Exception as e:
        logger.error(f"Database error getting streak status for user {user_id}: {e}")
        raise StreakError(f"Failed to get streak status: {str(e)}", 'STREAK_STATUS_ERROR')

