"""
Comprehensive pytest tests for the LearnQuest Admin API.

Tests cover:
- Admin access control (non-admin rejection)
- Dashboard statistics
- Pending path approvals/rejections
- User management (list, role change, suspend, delete)
- Content moderation (reports, dismiss, action)
"""

import pytest
from datetime import datetime, timedelta
from app.models.user import User
from app.models.learning_path import LearningPath
from app.models.report import Report, Notification
from app import db


class TestAdminAccessControl:
    """Tests for admin role requirement."""

    def test_non_admin_cannot_access_stats(self, test_client, auth_headers):
        """
        Test that non-admin users cannot access admin endpoints.
        
        Expected:
        - Status code: 403 Forbidden
        - Response contains error about admin access
        """
        response = test_client.get(
            '/api/admin/stats',
            headers=auth_headers
        )
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
        assert 'admin' in data['error'].lower()

    def test_unauthenticated_cannot_access_admin(self, test_client):
        """
        Test that unauthenticated requests are rejected.
        
        Expected:
        - Status code: 401 Unauthorized
        """
        response = test_client.get('/api/admin/stats')
        assert response.status_code == 401


class TestDashboardStats:
    """Tests for admin dashboard statistics."""

    def test_get_stats_success(self, test_client, admin_headers):
        """
        Test that admin can fetch dashboard statistics.
        
        Expected:
        - Status code: 200 OK
        - Response contains stats with expected fields
        """
        response = test_client.get(
            '/api/admin/stats',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'stats' in data
        
        stats = data['stats']
        assert 'total_users' in stats
        assert 'user_growth_percent' in stats
        assert 'total_learning_paths' in stats
        assert 'active_learners_today' in stats
        assert 'pending_approvals' in stats


class TestPendingApprovals:
    """Tests for learning path approval workflow."""

    def test_get_pending_paths(self, test_client, admin_headers, pending_path):
        """
        Test that admin can fetch pending learning paths.
        """
        response = test_client.get(
            '/api/admin/pending',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'pending_paths' in data
        assert len(data['pending_paths']) >= 1

    def test_approve_path(self, test_client, admin_headers, pending_path, app):
        """
        Test that admin can approve a learning path.
        
        Expected:
        - Path is_approved becomes True
        - Creator receives XP
        - Notification is created
        """
        response = test_client.post(
            f'/api/admin/approve/{pending_path.id}',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'xp_awarded' in data
        
        # Verify path is approved
        with app.app_context():
            path = LearningPath.query.get(pending_path.id)
            assert path.is_approved is True

    def test_reject_path(self, test_client, admin_headers, pending_path, app):
        """
        Test that admin can reject a learning path with reason.
        """
        response = test_client.post(
            f'/api/admin/reject/{pending_path.id}',
            headers=admin_headers,
            json={'reason': 'Content quality issues'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'reason' in data
        
        # Verify path is unpublished
        with app.app_context():
            path = LearningPath.query.get(pending_path.id)
            assert path.is_published is False

    def test_approve_nonexistent_path(self, test_client, admin_headers):
        """
        Test that approving nonexistent path returns 404.
        """
        response = test_client.post(
            '/api/admin/approve/99999',
            headers=admin_headers
        )
        
        assert response.status_code == 404


class TestUserManagement:
    """Tests for user management endpoints."""

    def test_get_users(self, test_client, admin_headers, test_user):
        """
        Test that admin can fetch user list.
        """
        response = test_client.get(
            '/api/admin/users',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'users' in data
        assert 'pagination' in data

    def test_get_users_with_search(self, test_client, admin_headers, test_user):
        """
        Test that user search works.
        """
        response = test_client.get(
            '/api/admin/users?search=testuser',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_get_users_filter_by_role(self, test_client, admin_headers):
        """
        Test that role filter works.
        """
        response = test_client.get(
            '/api/admin/users?role=learner',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_change_user_role(self, test_client, admin_headers, test_user, app):
        """
        Test that admin can change user role.
        """
        response = test_client.put(
            f'/api/admin/users/{test_user.id}/role',
            headers=admin_headers,
            json={'role': 'contributor'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        with app.app_context():
            user = User.query.get(test_user.id)
            assert user.role == 'contributor'

    def test_change_role_invalid(self, test_client, admin_headers, test_user):
        """
        Test that invalid role is rejected.
        """
        response = test_client.put(
            f'/api/admin/users/{test_user.id}/role',
            headers=admin_headers,
            json={'role': 'superadmin'}
        )
        
        assert response.status_code == 400

    def test_suspend_user(self, test_client, admin_headers, test_user, app):
        """
        Test that admin can suspend a user.
        """
        response = test_client.put(
            f'/api/admin/users/{test_user.id}/suspend',
            headers=admin_headers,
            json={'suspend': True}
        )
        
        assert response.status_code == 200
        
        with app.app_context():
            user = User.query.get(test_user.id)
            assert user.status == 'suspended'

    def test_delete_user(self, test_client, admin_headers, test_user, app):
        """
        Test that admin can delete a user.
        """
        user_id = test_user.id
        
        response = test_client.delete(
            f'/api/admin/users/{user_id}',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        
        with app.app_context():
            user = User.query.get(user_id)
            assert user is None

    def test_admin_cannot_delete_self(self, test_client, admin_headers, admin_user):
        """
        Test that admin cannot delete their own account.
        """
        response = test_client.delete(
            f'/api/admin/users/{admin_user.id}',
            headers=admin_headers
        )
        
        assert response.status_code == 400


class TestContentModeration:
    """Tests for content moderation endpoints."""

    def test_get_reports(self, test_client, admin_headers, test_report):
        """
        Test that admin can fetch reports.
        """
        response = test_client.get(
            '/api/admin/reports',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'reports' in data

    def test_dismiss_report(self, test_client, admin_headers, test_report, app):
        """
        Test that admin can dismiss a report.
        """
        response = test_client.post(
            f'/api/admin/reports/{test_report.id}/dismiss',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        
        with app.app_context():
            report = Report.query.get(test_report.id)
            assert report.status == 'dismissed'

    def test_action_report_warn(self, test_client, admin_headers, test_report, app):
        """
        Test that admin can take action on a report.
        """
        response = test_client.post(
            f'/api/admin/reports/{test_report.id}/action',
            headers=admin_headers,
            json={'action': 'warn', 'notes': 'First warning'}
        )
        
        assert response.status_code == 200
        
        with app.app_context():
            report = Report.query.get(test_report.id)
            assert report.status == 'actioned'
            assert report.action_taken == 'warn'

    def test_action_report_invalid(self, test_client, admin_headers, test_report):
        """
        Test that invalid action is rejected.
        """
        response = test_client.post(
            f'/api/admin/reports/{test_report.id}/action',
            headers=admin_headers,
            json={'action': 'invalid_action'}
        )
        
        assert response.status_code == 400


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def admin_user(app):
    """Create an admin user for testing."""
    with app.app_context():
        user = User(
            username='adminuser',
            email='admin@example.com',
            role='admin'
        )
        user.set_password('adminpassword123')
        db.session.add(user)
        db.session.commit()
        yield user


@pytest.fixture
def admin_headers(test_client, admin_user, app):
    """Get auth headers for admin user."""
    response = test_client.post(
        '/api/auth/login',
        json={
            'email': 'admin@example.com',
            'password': 'adminpassword123'
        }
    )
    data = response.get_json()
    return {
        'Authorization': f'Bearer {data["access_token"]}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def pending_path(app, test_user):
    """Create a pending learning path for testing."""
    with app.app_context():
        path = LearningPath(
            title='Test Pending Path',
            description='A path pending approval',
            category='Technology',
            difficulty='beginner',
            creator_id=test_user.id,
            is_published=True,
            is_approved=False
        )
        db.session.add(path)
        db.session.commit()
        yield path


@pytest.fixture
def test_report(app, test_user, admin_user):
    """Create a test report for moderation testing."""
    with app.app_context():
        report = Report(
            reporter_id=admin_user.id,
            content_type='comment',
            content_id=1,
            reason='spam',
            details='This is spam content',
            status='pending'
        )
        db.session.add(report)
        db.session.commit()
        yield report
