from __future__ import annotations

from flask import Blueprint, redirect, render_template, url_for

from ..services import build_context, current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    if not current_user():
        return redirect(url_for('auth.auth_page', tab='login'))
    return render_template('index.html', **build_context())
