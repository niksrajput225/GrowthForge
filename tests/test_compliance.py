from app.extensions import db
from app.models.user import User
from app.models.task import Task
from app.models.skill import SkillCategory
from app.models.note import Note

def test_privacy_policy_page(client):
    res = client.get('/privacy-policy')
    assert res.status_code == 200
    assert b"Privacy Policy" in res.data
    assert b"Google Play" in res.data

def test_terms_page(client):
    res = client.get('/terms')
    assert res.status_code == 200
    assert b"Terms of Service" in res.data

def test_web_account_deletion_page(client):
    res = client.get('/account/delete')
    assert res.status_code == 200
    assert b"Delete Account" in res.data

def test_api_account_deletion_cascade(app, client, test_user, auth_headers):
    # Verify user exists and has seeded tasks
    with app.app_context():
        user_id = test_user['user_id']
        tasks_count = Task.query.filter_by(user_id=user_id).count()
        skills_count = SkillCategory.query.filter_by(user_id=user_id).count()
        note = Note.query.filter_by(user_id=user_id).first()
        assert tasks_count > 0
        assert skills_count > 0
        assert note is not None

    # Call delete account API
    res = client.post('/api/v1/auth/delete-account', headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()['success'] is True

    # Verify cascading delete eliminated all associated data
    with app.app_context():
        assert db.session.get(User, user_id) is None
        assert Task.query.filter_by(user_id=user_id).count() == 0
        assert SkillCategory.query.filter_by(user_id=user_id).count() == 0
        assert Note.query.filter_by(user_id=user_id).first() is None
