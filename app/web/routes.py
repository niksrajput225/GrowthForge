from datetime import datetime, timezone
from sqlalchemy import text
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, limiter
from app.models.user import User
from app.api.auth import seed_new_user_data

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
@web_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@web_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("20 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))
        
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')
            
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_url = request.args.get('next')
            return redirect(next_url or url_for('web.dashboard'))
            
        flash('Invalid username or password.', 'error')
        
    return render_template('login.html')

@web_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))
        
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        email = (request.form.get('email') or '').strip().lower() or None
        
        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('register.html')
            
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
            return render_template('register.html')
            
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
            
        if User.query.filter_by(username=username).first():
            flash('Username is already taken.', 'error')
            return render_template('register.html')
            
        if email and User.query.filter_by(email=email).first():
            flash('Email is already registered.', 'error')
            return render_template('register.html')
            
        try:
            user = User(username=username, email=email, xp_points=100)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()
            seed_new_user_data(user)
            db.session.commit()
            
            login_user(user, remember=True)
            flash('Welcome to GrowthForge!', 'success')
            return redirect(url_for('web.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
            
    return render_template('register.html')

@web_bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('web.login'))

@web_bp.route('/health')
def health():
    """Application and database health check."""
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500
