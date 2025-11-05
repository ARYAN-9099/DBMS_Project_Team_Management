from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..extensions import mysql

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role', 'player')

            if not all([name, email, password]):
                flash('All fields are required!', 'danger')
                return redirect(url_for('auth.register_user'))

            if role not in ['admin', 'player', 'organizer']:
                flash('Invalid role selected!', 'danger')
                return redirect(url_for('auth.register_user'))

            cursor = mysql.connection.cursor()
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('Email already registered!', 'warning')
                cursor.close()
                return redirect(url_for('auth.register_user'))

            cursor.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
            """, (name, email, password, role))

            mysql.connection.commit()
            user_id = cursor.lastrowid
            cursor.close()

            flash(f'User registered successfully! User ID: {user_id}', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error registering user: {str(e)}', 'danger')
            return redirect(url_for('auth.register_user'))

    return render_template('register_user.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')

            if not all([email, password]):
                flash('Email and password are required!', 'danger')
                return redirect(url_for('auth.login'))

            cursor = mysql.connection.cursor()
            cursor.execute("""
                SELECT user_id, name, email, role 
                FROM users 
                WHERE email = %s AND password = %s
            """, (email, password))

            user = cursor.fetchone()
            cursor.close()

            if user:
                session['user_id'] = user['user_id']
                session['name'] = user['name']
                session['email'] = user['email']
                session['role'] = user['role']

                flash(f'Welcome, {user["name"]}!', 'success')
                return redirect(url_for('main.index'))

            flash('Invalid email or password!', 'danger')
            return redirect(url_for('auth.login'))

        except Exception as e:
            flash(f'Login error: {str(e)}', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))
