"""
Leaderboard Service for LearnQuest

Provides leaderboard functionality with support for different time periods
(daily, weekly, monthly, all_time) and user ranking information.

Uses SQLAlchemy queries on the User model.
"""

from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models.user import User
import logging

logger = logging.getLogger(__name__)


class LeaderboardError(Exception):
    """Custom exception for leaderboard-related errors."""
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


def get_leaderboard(period='all_time', limit=100):
    """
    Get the leaderboard for a specified time period.
    
    Args:
        period (str): Time period filter. Valid values:
            - 'daily': Filter users active today
            - 'weekly': Filter users active this week
            - 'monthly': Filter users active this month
            - 'all_time': All users (no time filter)
        limit (int): Maximum number of entries to return (default: 100)
    
    Returns:
        list: List of dictionaries containing leaderboard entries with:
            - rank (int): User's position on the leaderboard
            - user_id (int): User's ID
            - username (str): User's username
            - avatar_url (str): URL to user's avatar
            - xp (int): User's total XP
            - points (int): User's total points
    
    Raises:
        LeaderboardError: If a database error occurs or invalid period.
    """
    try:
        # Validate period
        valid_periods = ['daily', 'weekly', 'monthly', 'all_time']
        if period not in valid_periods:
            raise LeaderboardError(
                f"Invalid period '{period}'. Must be one of: {', '.join(valid_periods)}",
                'INVALID_PERIOD'
            )
        
        # Validate limit
        if limit < 1:
            limit = 1
        elif limit > 1000:
            limit = 1000
        
        # Build base query
        query = User.query
        
        # Apply time-based filtering based on last_active
        now = datetime.utcnow()
        
        if period == 'daily':
            # Active within the last 24 hours
            start_date = now - timedelta(days=1)
            query = query.filter(User.last_active >= start_date)
        
        elif period == 'weekly':
            # Active within the last 7 days
            start_date = now - timedelta(weeks=1)
            query = query.filter(User.last_active >= start_date)
        
        elif period == 'monthly':
            # Active within the last 30 days
            start_date = now - timedelta(days=30)
            query = query.filter(User.last_active >= start_date)
        
        # Order by XP descending and get top users
        top_users = query.order_by(User.xp.desc()).limit(limit).all()
        
        # Build leaderboard list
        leaderboard = []
        for rank, user in enumerate(top_users, 1):
            leaderboard.append({
                'rank': rank,
                'user_id': user.id,
                'username': user.username,
                'avatar_url': user.avatar_url,
                'xp': user.xp,
                'points': user.points
            })
        
        logger.debug(f"Retrieved leaderboard for period '{period}' with {len(leaderboard)} entries")
        
        return leaderboard
    
    except LeaderboardError:
        raise
    except Exception as e:
        logger.error(f"Database error retrieving leaderboard: {e}")
        raise LeaderboardError(f"Failed to retrieve leaderboard: {str(e)}", 'LEADERBOARD_ERROR')


def get_user_rank(user_id, period='all_time'):
    """
    Get a user's rank and surrounding users on the leaderboard.
    
    Args:
        user_id (int): The ID of the user to find.
        period (str): Time period filter. Valid values:
            - 'daily': Filter users active today
            - 'weekly': Filter users active this week
            - 'monthly': Filter users active this month
            - 'all_time': All users (no time filter)
    
    Returns:
        dict: Dictionary containing:
            - user_rank (int): The user's current rank (1-based)
            - user (dict): User details (id, username, avatar_url, xp, points)
            - surrounding_users (list): List of up to 2 users before and after
            - period (str): The period used for the query
            - total_users (int): Total number of users in the leaderboard
    
    Raises:
        LeaderboardError: If user not found, invalid period, or DB error.
    """
    try:
        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            raise LeaderboardError(f"User with ID {user_id} not found", 'USER_NOT_FOUND')
        
        # Validate period
        valid_periods = ['daily', 'weekly', 'monthly', 'all_time']
        if period not in valid_periods:
            raise LeaderboardError(
                f"Invalid period '{period}'. Must be one of: {', '.join(valid_periods)}",
                'INVALID_PERIOD'
            )
        
        # Build query for ranking
        query = User.query
        
        # Apply time-based filtering
        now = datetime.utcnow()
        
        if period == 'daily':
            start_date = now - timedelta(days=1)
            query = query.filter(User.last_active >= start_date)
        
        elif period == 'weekly':
            start_date = now - timedelta(weeks=1)
            query = query.filter(User.last_active >= start_date)
        
        elif period == 'monthly':
            start_date = now - timedelta(days=30)
            query = query.filter(User.last_active >= start_date)
        
        # Count total users in the filtered set
        total_users = query.count()
        
        # Get user's rank by counting users with higher XP
        # Subquery to count users with more XP
        users_with_higher_xp = query.filter(User.xp > user.xp).count()
        user_rank = users_with_higher_xp + 1
        
        # Get surrounding users (2 before, 2 after)
        surrounding_users = []
        
        # Get users ranked just above the current user
        users_above = query.filter(
            User.xp > user.xp
        ).order_by(
            User.xp.asc()
        ).limit(2).all()
        
        # Get users ranked just below the current user
        users_below = query.filter(
            User.xp < user.xp
        ).order_by(
            User.xp.desc()
        ).limit(2).all()
        
        # Build surrounding users list (ranked from higher to lower than user)
        for above_user in reversed(users_above):
            above_rank = query.filter(User.xp > above_user.xp).count() + 1
            surrounding_users.append({
                'rank': above_rank,
                'user_id': above_user.id,
                'username': above_user.username,
                'avatar_url': above_user.avatar_url,
                'xp': above_user.xp,
                'points': above_user.points,
                'position': 'above'
            })
        
        for below_user in users_below:
            below_rank = query.filter(User.xp > below_user.xp).count() + 1
            surrounding_users.append({
                'rank': below_rank,
                'user_id': below_user.id,
                'username': below_user.username,
                'avatar_url': below_user.avatar_url,
                'xp': below_user.xp,
                'points': below_user.points,
                'position': 'below'
            })
        
        result = {
            'user_rank': user_rank,
            'user': {
                'user_id': user.id,
                'username': user.username,
                'avatar_url': user.avatar_url,
                'xp': user.xp,
                'points': user.points
            },
            'surrounding_users': surrounding_users,
            'period': period,
            'total_users': total_users
        }
        
        logger.debug(f"User {user_id} rank: {user_rank} (period: {period})")
        
        return result
    
    except LeaderboardError:
        raise
    except Exception as e:
        logger.error(f"Database error getting user rank: {e}")
        raise LeaderboardError(f"Failed to get user rank: {str(e)}", 'RANK_ERROR')


def get_period_stats(period='all_time'):
    """
    Get statistics for a leaderboard period.
    
    Args:
        period (str): Time period filter.
    
    Returns:
        dict: Dictionary containing period statistics:
            - total_users (int): Number of active users
            - top_xp (int): Highest XP on the leaderboard
            - avg_xp (float): Average XP of users on leaderboard
    """
    try:
        query = User.query
        
        now = datetime.utcnow()
        
        if period == 'daily':
            start_date = now - timedelta(days=1)
            query = query.filter(User.last_active >= start_date)
        elif period == 'weekly':
            start_date = now - timedelta(weeks=1)
            query = query.filter(User.last_active >= start_date)
        elif period == 'monthly':
            start_date = now - timedelta(days=30)
            query = query.filter(User.last_active >= start_date)
        
        total_users = query.count()
        
        if total_users == 0:
            return {
                'total_users': 0,
                'top_xp': 0,
                'avg_xp': 0.0
            }
        
        # Get top XP
        top_user = query.order_by(User.xp.desc()).first()
        top_xp = top_user.xp if top_user else 0
        
        # Calculate average XP
        avg_xp = query.with_entities(func.avg(User.xp)).scalar() or 0.0
        
        return {
            'total_users': total_users,
            'top_xp': top_xp,
            'avg_xp': round(avg_xp, 2)
        }
    
    except Exception as e:
        logger.error(f"Database error getting period stats: {e}")
        raise LeaderboardError(f"Failed to get period stats: {str(e)}", 'STATS_ERROR')

