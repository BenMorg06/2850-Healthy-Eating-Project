from __future__ import annotations

from uuid import uuid4

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from ..db import execute, fetch_one
from ..services import current_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth')
def auth_page():
    if current_user():
        return redirect(url_for('main.home'))
    return render_template('auth.html', active_tab=request.args.get('tab', 'login'))


@auth_bp.post('/login')
def login():
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    user = fetch_one('SELECT * FROM users WHERE lower(email) = ?', (email,))
    if not user or not check_password_hash(user['password_hash'], password):
        flash('Invalid email or password.', 'error')
        return redirect(url_for('auth.auth_page', tab='login'))
    session['user_id'] = user['id']
    flash('Login successful.', 'success')
    return redirect(url_for('main.home'))


@auth_bp.post('/register')
def register():
    email = request.form.get('email', '').strip().lower()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    phone = request.form.get('phone', '').strip()
    gender = request.form.get('gender', '').strip()
    weight = request.form.get('weight', '').strip()

    if password != confirm_password:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('auth.auth_page', tab='register'))

    existing = fetch_one('SELECT id FROM users WHERE lower(email) = ?', (email,))
    if existing:
        flash('This email is already registered.', 'error')
        return redirect(url_for('auth.auth_page', tab='register'))

    execute(
        """
        INSERT INTO users (id, email, username, password_hash, phone, gender, weight, status, is_professional)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'New user', 0)
        """,
        (
            str(uuid4()),
            email,
            username,
            generate_password_hash(password),
            phone or None,
            gender or None,
            float(weight) if weight else None,
        ),
    )

    created_user = fetch_one('SELECT id FROM users WHERE lower(email) = ?', (email,))
    if created_user:
        session['user_id'] = created_user['id']
    flash('Account created successfully.', 'success')
    return redirect(url_for('main.home'))


@auth_bp.get('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'success')
    return redirect(url_for('auth.auth_page', tab='login'))
