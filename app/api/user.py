import os
from datetime import datetime, timezone
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app, url_for
from werkzeug.utils import secure_filename
from app.extensions import db, limiter, dual_auth_required
from app.models.task import Task, WeeklyTask
from app.models.skill import SkillCategory
from app.models.note import Note

user_bp = Blueprint('api_user', __name__, url_prefix='/api/v1/user')

def calculate_progress(items):
    if not items:
        return 0
    completed = sum(1 for i in items if i.completed)
    return int((completed / len(items)) * 100)

@user_bp.route('/summary', methods=['GET'])
@dual_auth_required
def get_user_summary():
    """Aggregates all user progress, tasks, skills, and notes into one fast response."""
    user = request.auth_user
    
    tasks = Task.query.filter_by(user_id=user.id).order_by(Task.completed.asc(), Task.created_at.desc()).all()
    weekly_tasks = WeeklyTask.query.filter_by(user_id=user.id).order_by(WeeklyTask.completed.asc(), WeeklyTask.created_at.desc()).all()
    categories = SkillCategory.query.filter_by(user_id=user.id).order_by(SkillCategory.created_at.asc()).all()
    note = Note.query.filter_by(user_id=user.id).first()
    
    daily_progress = calculate_progress(tasks)
    weekly_progress = calculate_progress(weekly_tasks)
    skills_data = [c.to_dict() for c in categories]
    
    all_scores = [daily_progress, weekly_progress]
    if skills_data:
        all_scores.extend([s['progress'] for s in skills_data])
    overall_progress = int(sum(all_scores) / len(all_scores)) if all_scores else 0
    
    return jsonify({
        'success': True,
        'user': user.to_dict(),
        'tasks': [t.to_dict() for t in tasks],
        'weekly_tasks': [w.to_dict() for w in weekly_tasks],
        'skills': skills_data,
        'note_content': note.content if note else '',
        'daily_progress': daily_progress,
        'weekly_progress': weekly_progress,
        'overall_progress': overall_progress,
        'completed_tasks_count': sum(1 for t in tasks if t.completed),
        'total_tasks_count': len(tasks)
    })

@user_bp.route('/avatar', methods=['POST'])
@dual_auth_required
@limiter.limit("10 per minute")
def upload_avatar():
    user = request.auth_user
    if 'avatar' not in request.files:
        return jsonify({'success': False, 'error': 'No file part in request.'}), 400
        
    file = request.files['avatar']
    if not file or file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected.'}), 400
        
    allowed_exts = current_app.config['ALLOWED_EXTENSIONS']
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_exts:
        return jsonify({
            'success': False,
            'error': f'Invalid image format. Allowed: {", ".join(allowed_exts)}'
        }), 400
        
    ext = file.filename.rsplit('.', 1)[1].lower()
    clean_name = f"user_{user.id}_{int(datetime.now(timezone.utc).timestamp())}.{ext}"
    upload_dir = Path(current_app.config['UPLOAD_FOLDER'])
    file_path = upload_dir / clean_name
    file.save(str(file_path))
    
    avatar_url = url_for('static', filename=f'uploads/{clean_name}', _external=False)
    user.avatar_url = avatar_url
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Avatar updated.',
        'avatar_url': avatar_url
    })
