from functools import wraps
from flask import Blueprint, request, session, redirect, url_for, jsonify, render_template, flash
from models.user import User

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'Authentication required. Please login.'}), 401
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'Authentication required.'}), 401
            return redirect(url_for('auth.login_page'))
        if session.get('role') != 'admin':
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'Access denied. Administrator privileges required.'}), 403
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('main_views.index_page'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if 'user_id' in session and request.method == 'GET':
        return redirect(url_for('main_views.index_page'))
        
    if request.method == 'POST':
        # Accept either JSON or Form Data
        if request.is_json:
            data = request.get_json() or {}
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
        else:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()

        if not username or not password:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Username and password are required.'}), 400
            flash('Username and password are required.', 'danger')
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            if request.is_json:
                return jsonify({'success': False, 'error': 'Invalid username or password.'}), 401
            flash('Invalid username or password.', 'danger')
            return render_template('login.html')

        # Authentication successful - establish session
        session['user_id'] = user.id
        session['username'] = user.username
        session['full_name'] = user.full_name
        session['role'] = user.role

        if request.is_json:
            return jsonify({
                'success': True,
                'message': f'Welcome back, {user.full_name}!',
                'redirect': url_for('main_views.index_page'),
                'user': user.to_dict()
            })
        return redirect(url_for('main_views.index_page'))

    return render_template('login.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    if request.is_json:
        return jsonify({'success': True, 'message': 'Logged out successfully.'})
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login_page'))

@auth_bp.route('/api/auth/me', methods=['GET'])
def current_user():
    if 'user_id' not in session:
        return jsonify({'authenticated': False}), 200
    return jsonify({
        'authenticated': True,
        'user': {
            'id': session.get('user_id'),
            'username': session.get('username'),
            'full_name': session.get('full_name'),
            'role': session.get('role')
        }
    })
