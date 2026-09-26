from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user, logout_user
from app.extensions import db, limiter
from app.models.user import User

legal_bp = Blueprint('legal', __name__)

@legal_bp.route('/privacy-policy')
def privacy_policy():
    """
    Public Privacy Policy strictly complying with Google Play Developer Policy
    and User Data Policy requirements.
    """
    return render_template('privacy.html')

@legal_bp.route('/terms')
def terms_of_service():
    """Public Terms of Service."""
    return render_template('terms.html')

@legal_bp.route('/account/delete', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def delete_account_web():
    """
    Web-based Account Deletion Flow mandated by Google Play:
    Developers must provide a public web URL where users can request
    account and associated data deletion without requiring the app.
    """
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        confirm_text = (request.form.get('confirm_text') or '').strip()
        
        if confirm_text != "DELETE":
            flash("Please type 'DELETE' in uppercase to confirm account deletion.", "error")
            return render_template('delete_account.html')
            
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if not user or not user.check_password(password):
            flash("Invalid credentials. Please verify your username and password.", "error")
            return render_template('delete_account.html')
            
        try:
            if current_user.is_authenticated and current_user.id == user.id:
                logout_user()
                
            db.session.delete(user)
            db.session.commit()
            flash("Your account and all associated data have been permanently deleted.", "success")
            return render_template('delete_account.html', deleted=True)
        except Exception as e:
            db.session.rollback()
            flash(f"Deletion failed: {str(e)}", "error")
            
    return render_template('delete_account.html', deleted=False)
