import pytest
from app import create_app
from app.extensions import db, create_token
from app.models.user import User
from app.api.auth import seed_new_user_data

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(username='forgertest', email='test@growthforge.app', xp_points=100)
        user.set_password('StrongPass123!')
        db.session.add(user)
        db.session.flush()
        seed_new_user_data(user)
        db.session.commit()
        
        # Reload fresh instance
        user = User.query.filter_by(username='forgertest').first()
        token = create_token(user.id, 'access')
        refresh = create_token(user.id, 'refresh')
        return {
            'user_id': user.id,
            'username': user.username,
            'password': 'StrongPass123!',
            'token': token,
            'refresh_token': refresh
        }

@pytest.fixture
def auth_headers(test_user):
    return {
        'Authorization': f"Bearer {test_user['token']}",
        'Content-Type': 'application/json'
    }
