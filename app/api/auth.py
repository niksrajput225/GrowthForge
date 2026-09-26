import os
from flask import Blueprint, request, jsonify, current_app
from app.extensions import db, limiter, create_token, decode_token, dual_auth_required
from app.models.user import User
from app.models.task import Task, WeeklyTask
from app.models.skill import SkillCategory, SkillModule, SkillLog
from app.models.note import Note

auth_bp = Blueprint('api_auth', __name__, url_prefix='/api/v1/auth')

def seed_new_user_data(user):
    """Seed initial welcoming tasks, skills, and notes for a new user."""
    default_tasks = [
        Task(user_id=user.id, title='Install GrowthForge on your Android device', priority='high', completed=True),
        Task(user_id=user.id, title='Review daily growth goals', priority='high', completed=False),
        Task(user_id=user.id, title='Log your first skill progression entry', priority='medium', completed=False)
    ]
    db.session.add_all(default_tasks)
    
    weekly = WeeklyTask(user_id=user.id, title='Achieve Level 2 Mastery this week', completed=False)
    db.session.add(weekly)
    
    cat1 = SkillCategory(user_id=user.id, name='Mobile Engineering', color_theme='cyan', icon='fa-code')
    cat2 = SkillCategory(user_id=user.id, name='Physical Fitness', color_theme='gold', icon='fa-dumbbell')
    db.session.add_all([cat1, cat2])
    db.session.flush()
    
    mod1 = SkillModule(category_id=cat1.id, title='Android & Capacitor')
    mod2 = SkillModule(category_id=cat2.id, title='Strength Training')
    db.session.add_all([mod1, mod2])
    db.session.flush()
    
    db.session.add_all([
        SkillLog(module_id=mod1.id, name='Play Store Guidelines', metric='Reviewed'),
        SkillLog(module_id=mod2.id, name='Morning Push-ups', metric='30 Reps')
    ])
    
    db.session.add(Note(
        user_id=user.id,
        content="Welcome to GrowthForge! Track your daily wins, expand your skill tree, and level up every day."
    ))

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("10 per minute")
def register():
    data = request.get_json(silent=True) or request.form
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    email = (data.get('email') or '').strip().lower() or None
    
    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password are required.'}), 400
    
    if len(username) < 3 or len(username) > 40:
        return jsonify({'success': False, 'error': 'Username must be between 3 and 40 characters.'}), 400
    
    if len(password) < 6:
        return jsonify({'success': False, 'error': 'Password must be at least 6 characters long.'}), 400
        
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'error': 'That username is already taken.'}), 409
        
    if email and User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'error': 'That email is already registered.'}), 409

    try:
        user = User(username=username, email=email, xp_points=100)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        seed_new_user_data(user)
        db.session.commit()
        
        access_token = create_token(user.id, 'access')
        refresh_token = create_token(user.id, 'refresh')
        
        return jsonify({
            'success': True,
            'message': 'Account registered successfully.',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("15 per minute")
def login():
    data = request.get_json(silent=True) or request.form
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    
    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password are required.'}), 400
        
    user = User.query.filter((User.username == username) | (User.email == username)).first()
    if not user or not user.check_password(password):
        return jsonify({'success': False, 'error': 'Invalid username or password.'}), 401
        
    access_token = create_token(user.id, 'access')
    refresh_token = create_token(user.id, 'refresh')
    
    return jsonify({
        'success': True,
        'message': 'Login successful.',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    })

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    data = request.get_json(silent=True) or {}
    refresh_token = data.get('refresh_token')
    if not refresh_token:
        return jsonify({'success': False, 'error': 'Refresh token required.'}), 400
        
    payload, err = decode_token(refresh_token, 'refresh')
    if err:
        return jsonify({'success': False, 'error': err}), 401
        
    user_id = int(payload['sub'])
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found.'}), 404
        
    new_access_token = create_token(user.id, 'access')
    return jsonify({
        'success': True,
        'access_token': new_access_token
    })

@auth_bp.route('/me', methods=['GET'])
@dual_auth_required
def me():
    return jsonify({
        'success': True,
        'user': request.auth_user.to_dict()
    })

@auth_bp.route('/delete-account', methods=['POST'])
@dual_auth_required
def delete_account():
    """
    Permanently delete account and all associated data.
    Strictly required for Google Play Store policy compliance.
    """
    user = request.auth_user
    user_id = user.id
    
    try:
        # Cascade delete is configured on SQLAlchemy models
        db.session.delete(user)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f'Account {user_id} and all associated data have been permanently removed.'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to delete account: {str(e)}'}), 500
