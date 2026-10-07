from flask import Blueprint, request, jsonify
from app.extensions import db, dual_auth_required
from app.models.skill import SkillCategory, SkillModule, SkillLog

skills_bp = Blueprint('api_skills', __name__, url_prefix='/api/v1/skills')

@skills_bp.route('', methods=['GET'])
@dual_auth_required
def get_skills():
    user = request.auth_user
    categories = SkillCategory.query.filter_by(user_id=user.id).order_by(SkillCategory.created_at.asc()).all()
    return jsonify({
        'success': True,
        'categories': [c.to_dict() for c in categories]
    })

@skills_bp.route('/categories', methods=['POST'])
@dual_auth_required
def create_category():
    user = request.auth_user
    data = request.get_json(silent=True) or request.form
    name = (data.get('name') or '').strip()
    
    if not name:
        return jsonify({'success': False, 'error': 'Category name is required.'}), 400
        
    color_theme = (data.get('color_theme') or 'cyan').strip().lower()
    icon = (data.get('icon') or 'fa-star').strip()
    
    category = SkillCategory(
        user_id=user.id,
        name=name,
        color_theme=color_theme,
        icon=icon
    )
    db.session.add(category)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Skill category created.',
        'category': category.to_dict()
    }), 201

@skills_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
@dual_auth_required
def delete_category(cat_id):
    user = request.auth_user
    category = SkillCategory.query.filter_by(id=cat_id, user_id=user.id).first_or_404()
    db.session.delete(category)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Category deleted.'})

@skills_bp.route('/modules', methods=['POST'])
@dual_auth_required
def create_module():
    user = request.auth_user
    data = request.get_json(silent=True) or request.form
    title = (data.get('title') or '').strip()
    raw_cat_id = data.get('category_id')
    
    if not title or raw_cat_id is None:
        return jsonify({'success': False, 'error': 'Title and category_id are required.'}), 400
        
    try:
        category_id = int(raw_cat_id)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid category_id. Must be an integer.'}), 400
        
    category = db.session.get(SkillCategory, category_id)
    if not category or category.user_id != user.id:
        return jsonify({'success': False, 'error': 'Category not found.'}), 404
        
    try:
        module = SkillModule(category_id=category.id, title=title)
        db.session.add(module)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Module created.',
            'module': module.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to create module: {str(e)}'}), 500

@skills_bp.route('/modules/<int:mod_id>', methods=['DELETE'])
@dual_auth_required
def delete_module(mod_id):
    user = request.auth_user
    module = db.session.get(SkillModule, mod_id)
    if not module or not module.category or module.category.user_id != user.id:
        return jsonify({'success': False, 'error': 'Module not found.'}), 404
    
    try:
        db.session.delete(module)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Module deleted.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@skills_bp.route('/logs', methods=['POST'])
@dual_auth_required
def create_log():
    user = request.auth_user
    data = request.get_json(silent=True) or request.form
    name = (data.get('name') or '').strip()
    metric = (data.get('metric') or '').strip()
    raw_mod_id = data.get('module_id')
    
    if not name or not metric or raw_mod_id is None:
        return jsonify({'success': False, 'error': 'Name, metric, and module_id are required.'}), 400
        
    try:
        module_id = int(raw_mod_id)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid module_id. Must be an integer.'}), 400
        
    module = db.session.get(SkillModule, module_id)
    if not module or not module.category or module.category.user_id != user.id:
        return jsonify({'success': False, 'error': 'Module not found.'}), 404
        
    try:
        log = SkillLog(module_id=module.id, name=name, metric=metric)
        db.session.add(log)
        user.add_xp(10)  # +10 XP for logging progress
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Skill log added.',
            'log': log.to_dict(),
            'user_xp': user.xp_points,
            'user_level': user.level
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to add log: {str(e)}'}), 500

@skills_bp.route('/logs/<int:log_id>', methods=['DELETE'])
@dual_auth_required
def delete_log(log_id):
    user = request.auth_user
    log = db.session.get(SkillLog, log_id)
    if not log or not log.module or not log.module.category or log.module.category.user_id != user.id:
        return jsonify({'success': False, 'error': 'Log not found.'}), 404
    
    try:
        db.session.delete(log)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Skill log deleted.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
