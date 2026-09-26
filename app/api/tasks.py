from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from app.extensions import db, dual_auth_required
from app.models.task import Task, WeeklyTask

tasks_bp = Blueprint('api_tasks', __name__, url_prefix='/api/v1/tasks')

# --- Daily Tasks ---
@tasks_bp.route('', methods=['GET'])
@dual_auth_required
def list_tasks():
    user = request.auth_user
    query = Task.query.filter_by(user_id=user.id)
    
    completed = request.args.get('completed')
    if completed is not None:
        is_completed = completed.lower() in ['true', '1', 'yes']
        query = query.filter_by(completed=is_completed)
        
    priority = request.args.get('priority')
    if priority:
        query = query.filter_by(priority=priority.lower())
        
    tasks = query.order_by(Task.completed.asc(), Task.created_at.desc()).all()
    return jsonify({
        'success': True,
        'tasks': [t.to_dict() for t in tasks]
    })

@tasks_bp.route('', methods=['POST'])
@dual_auth_required
def create_task():
    user = request.auth_user
    data = request.get_json(silent=True) or request.form
    title = (data.get('title') or '').strip()
    
    if not title:
        return jsonify({'success': False, 'error': 'Task title is required.'}), 400
        
    task = Task(
        user_id=user.id,
        title=title,
        owner=(data.get('owner') or 'Personal').strip(),
        priority=(data.get('priority') or 'medium').lower(),
        category=(data.get('category') or 'General').strip()
    )
    db.session.add(task)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Task created.',
        'task': task.to_dict()
    }), 201

@tasks_bp.route('/<int:task_id>/toggle', methods=['POST'])
@dual_auth_required
def toggle_task(task_id):
    user = request.auth_user
    task = Task.query.filter_by(id=task_id, user_id=user.id).first_or_404()
    
    task.completed = not task.completed
    if task.completed:
        task.completed_at = datetime.now(timezone.utc)
        user.add_xp(15)  # Award +15 XP for finishing task
    else:
        task.completed_at = None
        user.add_xp(-15)
        
    db.session.commit()
    return jsonify({
        'success': True,
        'completed': task.completed,
        'user_xp': user.xp_points,
        'user_level': user.level
    })

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@dual_auth_required
def delete_task(task_id):
    user = request.auth_user
    task = Task.query.filter_by(id=task_id, user_id=user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Task deleted.'})

# --- Weekly Tasks ---
@tasks_bp.route('/weekly', methods=['GET'])
@dual_auth_required
def list_weekly():
    user = request.auth_user
    weekly = WeeklyTask.query.filter_by(user_id=user.id).order_by(WeeklyTask.completed.asc(), WeeklyTask.created_at.desc()).all()
    return jsonify({
        'success': True,
        'weekly_tasks': [w.to_dict() for w in weekly]
    })

@tasks_bp.route('/weekly', methods=['POST'])
@dual_auth_required
def create_weekly():
    user = request.auth_user
    data = request.get_json(silent=True) or request.form
    title = (data.get('title') or '').strip()
    
    if not title:
        return jsonify({'success': False, 'error': 'Weekly goal title is required.'}), 400
        
    weekly = WeeklyTask(user_id=user.id, title=title)
    db.session.add(weekly)
    db.session.commit()
    return jsonify({
        'success': True,
        'weekly_task': weekly.to_dict()
    }), 201

@tasks_bp.route('/weekly/<int:task_id>/toggle', methods=['POST'])
@dual_auth_required
def toggle_weekly(task_id):
    user = request.auth_user
    task = WeeklyTask.query.filter_by(id=task_id, user_id=user.id).first_or_404()
    
    task.completed = not task.completed
    if task.completed:
        task.completed_at = datetime.now(timezone.utc)
        user.add_xp(30)  # +30 XP for weekly milestone
    else:
        task.completed_at = None
        user.add_xp(-30)
        
    db.session.commit()
    return jsonify({
        'success': True,
        'completed': task.completed,
        'user_xp': user.xp_points,
        'user_level': user.level
    })

@tasks_bp.route('/weekly/<int:task_id>', methods=['DELETE'])
@dual_auth_required
def delete_weekly(task_id):
    user = request.auth_user
    task = WeeklyTask.query.filter_by(id=task_id, user_id=user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Weekly goal deleted.'})
