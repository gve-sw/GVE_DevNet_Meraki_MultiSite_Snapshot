import functools
from src.db import get_db
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """

    :return:
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Username does not exist!'
        elif not check_password_hash(user['password'], password):
            error = 'Invalid Password!'

        # Success
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('blog.home'))
        # Error
        flash(error)
    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    """

    :return:
    """
    session.clear()
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """

    :return:
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        accessToken = request.form['X_CISCO_MERAKI_API_KEY']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not accessToken:
            error = 'API Key is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        # Success
        if error is None:
            db.execute(
                'INSERT INTO user (username, password, accessToken) VALUES (?, ?, ?)',
                (username, generate_password_hash(password), accessToken)
            )
            db.commit()
            return redirect(url_for('blog.home'))
        # Error
        flash(error)
    return render_template('auth/register.html')


@bp.before_app_request
def load_logged_in_user():
    """

    :return:
    """
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


def login_required(view):
    """

    :param view:
    :return:
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

