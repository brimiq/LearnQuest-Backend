import pytest
from app import db
from app.models.comment import Comment
from app.models.learning_path import LearningPath
import json

@pytest.fixture
def learning_path_id(app, test_user):
    """Create a test learning path and return its ID"""
    with app.app_context():
        user = db.session.merge(test_user)
        lp = LearningPath(
            title="Test Path",
            creator_id=user.id,
            is_published=True
        )
        db.session.add(lp)
        db.session.commit()
        return lp.id

def test_create_comment(test_client, auth_headers, learning_path_id):
    """Test creating a comment"""
    data = {
        'content': 'This is a test comment',
        'learning_path_id': learning_path_id
    }
    
    response = test_client.post(
        '/api/comments',
        headers=auth_headers,
        data=json.dumps(data)
    )
    
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['content'] == 'This is a test comment'
    assert json_data['learning_path_id'] == learning_path_id

def test_get_comments(test_client, auth_headers, learning_path_id):
    """Test listing comments"""
    # Create a comment first
    test_client.post(
        '/api/comments',
        headers=auth_headers,
        data=json.dumps({
            'content': 'First comment',
            'learning_path_id': learning_path_id
        })
    )
    
    response = test_client.get(
        f'/api/comments?learning_path_id={learning_path_id}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data['comments']) == 1
    assert json_data['comments'][0]['content'] == 'First comment'

def test_reply_comment(test_client, auth_headers, learning_path_id):
    """Test replying to a comment"""
    # Create parent
    res = test_client.post(
        '/api/comments',
        headers=auth_headers,
        data=json.dumps({
            'content': 'Parent comment',
            'learning_path_id': learning_path_id
        })
    )
    parent_id = res.get_json()['id']
    
    # Reply
    response = test_client.post(
        '/api/comments',
        headers=auth_headers,
        data=json.dumps({
            'content': 'Reply comment',
            'learning_path_id': learning_path_id,
            'parent_id': parent_id
        })
    )
    
    assert response.status_code == 201
    
    # Verify nesting
    response = test_client.get(
        f'/api/comments?learning_path_id={learning_path_id}',
        headers=auth_headers
    )
    comments = response.get_json()['comments']
    parent = next(c for c in comments if c['id'] == parent_id)
    assert len(parent['replies']) == 1
    assert parent['replies'][0]['content'] == 'Reply comment'

def test_edit_comment(test_client, auth_headers, learning_path_id):
    """Test editing a comment"""
    res = test_client.post(
        '/api/comments',
        headers=auth_headers,
        data=json.dumps({
            'content': 'Original content',
            'learning_path_id': learning_path_id
        })
    )
    comment_id = res.get_json()['id']
    
    response = test_client.put(
        f'/api/comments/{comment_id}',
        headers=auth_headers,
        data=json.dumps({
            'content': 'Updated content'
        })
    )
    
    assert response.status_code == 200
    assert response.get_json()['content'] == 'Updated content'

def test_delete_comment(test_client, auth_headers, learning_path_id):
    """Test soft delete comment"""
    res = test_client.post(
        '/api/comments',
        headers=auth_headers,
        data=json.dumps({
            'content': 'To be deleted',
            'learning_path_id': learning_path_id
        })
    )
    comment_id = res.get_json()['id']
    
    response = test_client.delete(
        f'/api/comments/{comment_id}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Verify masked content in list
    response = test_client.get(
        f'/api/comments?learning_path_id={learning_path_id}',
        headers=auth_headers
    )
    comments = response.get_json()['comments']
    comment = next(c for c in comments if c['id'] == comment_id)
    assert comment['is_deleted'] is True
    assert comment['content'] == '[This comment has been deleted]'
