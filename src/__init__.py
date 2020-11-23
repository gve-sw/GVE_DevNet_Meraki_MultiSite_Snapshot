import os
from . import db, auth, blog
from flask import Flask


def create_app(test_config=None):
    """
    Prototype Initialization (Factory Method)
    :param test_config:
    :return:
    """
    # Create and Configure Prototype Instance
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        db.init_app(app)
        app.register_blueprint(auth.bp)

        app.register_blueprint(blog.bp)
        app.add_url_rule('/', endpoint='index')

        # a simple page that says hello
        @app.route('/hello')
        def hello():
            return 'Hello, World!'

        return app
