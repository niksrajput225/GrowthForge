from flask import Blueprint
from app.api.auth import auth_bp
from app.api.tasks import tasks_bp
from app.api.skills import skills_bp
from app.api.notes import notes_bp
from app.api.user import user_bp

def register_api_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(user_bp)
