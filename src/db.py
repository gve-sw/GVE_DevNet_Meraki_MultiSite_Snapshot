import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext


def init_app(app):
    """
    Register Prototype Context to Database
    :param app: Prototype
    :return:
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


@click.command('init-db')
@with_appcontext
def init_db_command():
    """
    Clear the existing data and create new tables.
    :return:
    """
    init_db()
    click.echo('Database Initialized!')


def init_db():
    """
    Initialize Prototype Database
    :return:
    """
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def get_db():
    """
    Retrieve / Establish connection to Database
    :return:
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """
    Close connection to Database
    :param e:
    :return:
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()
