import jwt
from datetime import datetime, timezone
from functools import wraps
from flask import request, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'web.login'
login_manager.login_message = 'Please sign in to access your dashboard.'
login_manager.login_message_category = 'info'

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    default_limits=["300 per day", "100 per hour"]
)

cors = CORS()

# --- JWT Security Helpers for Mobile & API ---
def create_token(user_id, token_type='access'):
    """Generate signed JWT token."""
    now = datetime.now(timezone.utc)
    if token_type == 'access':
        expires_delta = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES')
    else:
        expires_delta = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES')
        
    payload = {
        'sub': str(user_id),
        'type': token_type,
        'iat': now,
        'exp': now + expires_delta
    }
    secret = current_app.config['JWT_SECRET_KEY']
    return jwt.encode(payload, secret, algorithm='HS256')

def decode_token(token, token_type='access'):
    """Decode and validate a JWT token."""
    try:
        secret = current_app.config['JWT_SECRET_KEY']
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        if payload.get('type') != token_type:
            return None, 'Invalid token type'
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, 'Token has expired'
    except jwt.InvalidTokenError as e:
        return None, f'Invalid token: {str(e)}'

def dual_auth_required(f):
    """
    Decorator that authenticates via either:
    1. Authorization: Bearer <jwt_token> (Primary for Android/Capacitor mobile client)
    2. Flask-Login Session Cookie (Primary for web browser client)
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        from app.models.user import User
        
        # 1. Check Bearer Token first
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()
            payload, err = decode_token(token, token_type='access')
            if err:
                return jsonify({'success': False, 'error': f'Authentication failed: {err}'}), 401
            
            user_id = int(payload['sub'])
            user = db.session.get(User, user_id)
            if not user or not user.is_active:
                return jsonify({'success': False, 'error': 'User not found or disabled'}), 401
            
            # Attach user to request context
            request.auth_user = user
            return f(*args, **kwargs)
        
        # 2. Check Flask-Login session
        if current_user.is_authenticated:
            request.auth_user = current_user
            return f(*args, **kwargs)
            
        return jsonify({
            'success': False,
            'error': 'Authentication required. Provide Bearer token or log in.'
        }), 401
    
    return decorated
