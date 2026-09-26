from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from app.extensions import db, dual_auth_required
from app.models.note import Note

notes_bp = Blueprint('api_notes', __name__, url_prefix='/api/v1/notes')

@notes_bp.route('', methods=['GET'])
@dual_auth_required
def get_note():
    user = request.auth_user
    note = Note.query.filter_by(user_id=user.id).first()
    return jsonify({
        'success': True,
        'note': note.to_dict() if note else {'content': '', 'updated_at': None}
    })

@notes_bp.route('', methods=['POST'])
@dual_auth_required
def save_note():
    user = request.auth_user
    data = request.get_json(silent=True) or request.form
    content = data.get('content', '')
    
    note = Note.query.filter_by(user_id=user.id).first()
    if not note:
        note = Note(user_id=user.id)
        db.session.add(note)
        
    note.content = content
    note.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Note saved.',
        'note': note.to_dict()
    })
