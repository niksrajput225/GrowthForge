import os
from flask import Flask, jsonify, render_template, request
from app.config import config_by_name
from app.extensions import db, migrate, login_manager, limiter, cors
from app.models.user import User

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
        
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))
    
    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    limiter.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    
    # Register Blueprints
    from app.api import register_api_blueprints
    from app.web import register_web_blueprints
    register_api_blueprints(app)
    register_web_blueprints(app)
    
    # Security Headers Hook
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
        
    # Global Error Handlers
    @app.errorhandler(400)
    def bad_request(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Bad request', 'details': str(e)}), 400
        return render_template('404.html', error='Bad request'), 400

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Resource not found'}), 404
        return render_template('404.html'), 404

    @app.errorhandler(429)
    def ratelimit_handler(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Rate limit exceeded. Please slow down.'}), 429
        return render_template('500.html', error='Rate limit exceeded. Please try again shortly.'), 429

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
        return render_template('500.html'), 500

    with app.app_context():
        # Ensure tables exist
        db.create_all()

    return app
