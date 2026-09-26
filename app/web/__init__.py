from app.web.routes import web_bp
from app.web.legal import legal_bp

def register_web_blueprints(app):
    app.register_blueprint(web_bp)
    app.register_blueprint(legal_bp)
