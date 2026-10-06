from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from database.connection import get_db_cursor
from services.auth_service import AuthService
from mysql.connector import Error
from functools import wraps
import re

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('auth.login'))
            if session.get('user_role') not in roles:
                flash('Access denied: You do not have permission to view this resource.', 'danger')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        login_input = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember_me = request.form.get('remember_me')
        
        if not login_input or not password:
            flash('Please fill in both username/email and password fields.', 'danger')
            return render_template('login.html')
            
        try:
            with get_db_cursor() as cursor:
                # Allow login with either username OR email
                cursor.execute("""
                    SELECT id, username, email, password_hash, full_name, role 
                    FROM users 
                    WHERE username = %s OR email = %s
                """, (login_input, login_input))
                user = cursor.fetchone()
                
                if user and check_password_hash(user['password_hash'], password):
                    session.clear()
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['user_fullname'] = user['full_name']
                    session['user_role'] = user['role']
                    
                    if remember_me:
                        session.permanent = True
                        
                    flash(f'Welcome back, {user["full_name"]}!', 'success')
                    
                    next_page = request.args.get('next')
                    # Validate next_page to prevent open redirect vulnerabilities
                    if next_page and next_page.startswith('/'):
                        return redirect(next_page)
                    return redirect(url_for('dashboard.index'))
                else:
                    # Anti-enumeration generic error message
                    flash('Invalid username/email or password. Please check your credentials.', 'danger')
        except Exception as e:
            flash(f'Database connection error: {str(e)}', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        requested_role = request.form.get('role', 'Receptionist').strip()
        
        # Public registration restriction: Do not permit self-assigning Admin role
        allowed_roles = ['Receptionist', 'Doctor']
        role = requested_role if requested_role in allowed_roles else 'Receptionist'
        
        # Validation checks
        if not full_name or not username or not email or not password or not confirm_password:
            flash('Please fill in all mandatory registration fields.', 'danger')
            return render_template('signup.html', form=request.form)
            
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            flash('Please provide a valid email address.', 'danger')
            return render_template('signup.html', form=request.form)
            
        if password != confirm_password:
            flash('Password confirmation does not match.', 'danger')
            return render_template('signup.html', form=request.form)
            
        if len(password) < 6:
            flash('Password must be at least 6 characters in length.', 'danger')
            return render_template('signup.html', form=request.form)
            
        try:
            with get_db_cursor(commit=False) as cursor:
                # Check for existing duplicate username or email
                cursor.execute("SELECT id, username, email FROM users WHERE username = %s OR email = %s", (username, email))
                existing = cursor.fetchone()
                
                if existing:
                    if existing['username'].lower() == username.lower():
                        flash('Username is already taken. Please choose another.', 'danger')
                    else:
                        flash('An account with this email address already exists.', 'danger')
                    return render_template('signup.html', form=request.form)
                    
                password_hash = generate_password_hash(password)
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, full_name, role)
                    VALUES (%s, %s, %s, %s, %s)
                """, (username, email, password_hash, full_name, role))
                
                cursor.execute("COMMIT")
                flash('Account created successfully! You may now log in.', 'success')
                return redirect(url_for('auth.login'))
        except Error as err:
            flash(f'Registration error: {str(err)}', 'danger')
            
    return render_template('signup.html', form=None)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email or not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            flash('Please provide a valid email address.', 'danger')
            return render_template('forgot_password.html')
            
        try:
            with get_db_cursor() as cursor:
                cursor.execute("SELECT id, email, username FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                
                if user:
                    raw_token = AuthService.create_reset_token(user['id'])
                    reset_url = url_for('auth.reset_password', token=raw_token, _external=True)
                    AuthService.send_reset_email(user['email'], reset_url)
        except Exception as e:
            # Log server error safely without exposing details to user
            pass
            
        # Generic confirmation message to avoid user enumeration
        flash('If an account exists for that email address, password reset instructions have been sent.', 'info')
        return redirect(url_for('auth.login'))
        
    return render_template('forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    is_valid, record_or_msg = AuthService.validate_reset_token(token)
    
    if not is_valid:
        flash(record_or_msg, 'danger')
        return render_template('forgot_password.html')
        
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not password or not confirm_password:
            flash('Please fill in both new password fields.', 'danger')
            return render_template('reset_password.html', token=token)
            
        if password != confirm_password:
            flash('New password confirmation does not match.', 'danger')
            return render_template('reset_password.html', token=token)
            
        if len(password) < 6:
            flash('Password must be at least 6 characters in length.', 'danger')
            return render_template('reset_password.html', token=token)
            
        success, message = AuthService.reset_password(token, password)
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'danger')
            
    return render_template('reset_password.html', token=token)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not current_password or not new_password or not confirm_password:
            flash('Please fill in all password fields.', 'danger')
            return render_template('change_password.html')
            
        if new_password != confirm_password:
            flash('New password confirmation does not match.', 'danger')
            return render_template('change_password.html')
            
        if len(new_password) < 6:
            flash('New password must be at least 6 characters in length.', 'danger')
            return render_template('change_password.html')
            
        user_id = session.get('user_id')
        try:
            with get_db_cursor(commit=False) as cursor:
                cursor.execute("SELECT id, password_hash FROM users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
                
                if not user or not check_password_hash(user['password_hash'], current_password):
                    flash('Incorrect current password. Please try again.', 'danger')
                    return render_template('change_password.html')
                    
                new_hash = generate_password_hash(new_password)
                cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user_id))
                cursor.execute("COMMIT")
                
                session.clear()
                flash('Your password has been changed successfully. Please log in with your new password.', 'success')
                return redirect(url_for('auth.login'))
        except Error as err:
            flash(f'Failed to change password: {str(err)}', 'danger')
            
    return render_template('change_password.html')
