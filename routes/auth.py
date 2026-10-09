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

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration endpoint for new staff or admin users."""
    if 'user_id' in session and request.method == 'GET':
        return redirect(url_for('main_views.index_page'))

    if request.method == 'POST':
        if request.is_json:
            data = request.get_json() or {}
        else:
            data = request.form

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        full_name = data.get('full_name', '').strip()
        password = data.get('password', '').strip()
        role = data.get('role', 'staff').strip().lower()

        # Validation
        if not username or not password or not full_name:
            err_msg = 'Username, full name, and password are required.'
            if request.is_json:
                return jsonify({'success': False, 'error': err_msg}), 400
            flash(err_msg, 'danger')
            return render_template('register.html')

        if len(password) < 6:
            err_msg = 'Password must be at least 6 characters long.'
            if request.is_json:
                return jsonify({'success': False, 'error': err_msg}), 400
            flash(err_msg, 'danger')
            return render_template('register.html')

        if email and ('@' not in email or '.' not in email):
            err_msg = 'Please enter a valid email address.'
            if request.is_json:
                return jsonify({'success': False, 'error': err_msg}), 400
            flash(err_msg, 'danger')
            return render_template('register.html')

        # Check for duplicate username
        if User.query.filter_by(username=username).first():
            err_msg = f"Username '{username}' is already taken."
            if request.is_json:
                return jsonify({'success': False, 'error': err_msg}), 409
            flash(err_msg, 'danger')
            return render_template('register.html')

        # Check for duplicate email
        if email and User.query.filter_by(email=email).first():
            err_msg = f"An account with email '{email}' already exists."
            if request.is_json:
                return jsonify({'success': False, 'error': err_msg}), 409
            flash(err_msg, 'danger')
            return render_template('register.html')

        # Role enforcement: only existing admins can register admins, otherwise default to staff
        if role not in ('admin', 'staff'):
            role = 'staff'
        if role == 'admin' and session.get('role') != 'admin':
            role = 'staff'

        from models import db
        new_user = User(
            username=username,
            email=email if email else None,
            full_name=full_name,
            role=role
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Account created successfully! Please login.',
                'user': new_user.to_dict()
            }), 201

        flash('Registration successful! Please sign in with your credentials.', 'success')
        return redirect(url_for('auth.login_page'))

    return render_template('register.html')

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

# Admin User Management API
@auth_bp.route('/api/users', methods=['GET'])
@admin_required
def list_users():
    users = User.query.order_by(User.id.asc()).all()
    return jsonify({
        'success': True,
        'count': len(users),
        'users': [u.to_dict() for u in users]
    })

@auth_bp.route('/api/users', methods=['POST'])
@admin_required
def admin_create_user():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    full_name = data.get('full_name', '').strip()
    password = data.get('password', '').strip()
    email = data.get('email', '').strip()
    role = data.get('role', 'staff').strip().lower()

    if not username or not password or not full_name:
        return jsonify({'success': False, 'error': 'Username, full name, and password are required.'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'error': f"Username '{username}' already exists."}), 409

    if role not in ('admin', 'staff'):
        role = 'staff'

    from models import db
    user = User(username=username, email=email or None, full_name=full_name, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"User '{username}' created successfully.",
        'user': user.to_dict()
    }), 201

@auth_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    from models import db
    if session.get('user_id') == user_id:
        return jsonify({'success': False, 'error': 'You cannot delete your own active administrator account.'}), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found.'}), 404

    username = user.username
    db.session.delete(user)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"User '{username}' deleted successfully."
    })
