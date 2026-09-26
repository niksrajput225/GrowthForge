from datetime import datetime, timezone
from app.extensions import db

class SkillCategory(db.Model):
    __tablename__ = 'skill_categories'
    __table_args__ = (
        db.Index('idx_skill_user', 'user_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    icon = db.Column(db.String(50), default='fa-star')
    color_theme = db.Column(db.String(30), default='cyan')  # cyan, gold, emerald, violet, crimson
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    modules = db.relationship('SkillModule', backref='category', cascade='all, delete-orphan', lazy='joined')
    
    def to_dict(self):
        mods = [m.to_dict() for m in self.modules]
        total_logs = sum(len(m.get('logs', [])) for m in mods)
        progress = min(100, total_logs * 25)
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'color_theme': self.color_theme,
            'logs_count': total_logs,
            'progress': progress,
            'modules': mods,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SkillModule(db.Model):
    __tablename__ = 'skill_modules'
    __table_args__ = (
        db.Index('idx_module_cat', 'category_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('skill_categories.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    logs = db.relationship('SkillLog', backref='module', cascade='all, delete-orphan', lazy='joined')
    
    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'title': self.title,
            'logs': [l.to_dict() for l in self.logs],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SkillLog(db.Model):
    __tablename__ = 'skill_logs'
    __table_args__ = (
        db.Index('idx_log_module', 'module_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('skill_modules.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    metric = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'module_id': self.module_id,
            'name': self.name,
            'metric': self.metric,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
