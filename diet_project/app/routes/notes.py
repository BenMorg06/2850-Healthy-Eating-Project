from __future__ import annotations

from uuid import uuid4

from flask import Blueprint, flash, redirect, request, url_for

from ..db import execute
from ..helpers import login_required, today_str
from ..services import current_user

notes_bp = Blueprint('notes', __name__)


@notes_bp.post('/send-note')
@login_required
def send_note():
    client_id = request.form.get('client_id', '')
    note_text = request.form.get('note_text', '').strip()
    note_date = request.form.get('professional_date', today_str())
    if not note_text:
        flash('Please enter a note.', 'error')
        return redirect(url_for('main.home', page='professional', client_id=client_id, professional_date=note_date))
    execute(
        "INSERT INTO notes (id, client_id, author, message, date, read_by_client) VALUES (?, ?, 'Professional', ?, ?, 0)",
        (str(uuid4()), client_id, note_text, note_date),
    )
    flash('Note sent successfully.', 'success')
    return redirect(url_for('main.home', page='professional', client_id=client_id, professional_date=note_date))


@notes_bp.post('/mark-notes-read')
@login_required
def mark_notes_read():
    user = current_user()
    execute('UPDATE notes SET read_by_client = 1 WHERE client_id = ?', (user['id'],))
    return redirect(url_for('main.home', page='dashboard'))
