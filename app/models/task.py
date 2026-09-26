from datetime import datetime, timezone
from app.extensions import db

class Task(db.Model):
    __tablename__ = 'tasks'
    __table_args__ = (
        db.Index('idx_tasks_user_completed', 'user_id', 'completed'),
        db.Index('idx_tasks_user_priority', 'user_id', 'priority'),
        db.Index('idx_tasks_user_created', 'user_id', 'created_at'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    owner = db.Column(db.String(100), default='Personal')
    completed = db.Column(db.Boolean, default=False, index=True)
    priority = db.Column(db.String(20), default='medium')  # high, medium, low
    category = db.Column(db.String(50), default='General')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'owner': self.owner,
            'completed': self.completed,
            'priority': self.priority,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class WeeklyTask(db.Model):
    __tablename__ = 'weekly_tasks'
    __table_args__ = (
        db.Index('idx_weekly_user_completed', 'user_id', 'completed'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
