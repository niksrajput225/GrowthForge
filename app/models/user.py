from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_url = db.Column(db.String(350), default='https://api.dicebear.com/7.x/bottts/svg?seed=growthforge')
    is_active = db.Column(db.Boolean, default=True)
    streak_count = db.Column(db.Integer, default=1)
    xp_points = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships with strict cascade deletion for Google Play data deletion compliance
    tasks = db.relationship('Task', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    weekly_tasks = db.relationship('WeeklyTask', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    skill_categories = db.relationship('SkillCategory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def add_xp(self, amount):
        self.xp_points = (self.xp_points or 0) + amount
        
    @property
    def level(self):
        # 100 XP per level
        return max(1, (self.xp_points or 0) // 100)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'streak_count': self.streak_count,
            'xp_points': self.xp_points,
            'level': self.level,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
