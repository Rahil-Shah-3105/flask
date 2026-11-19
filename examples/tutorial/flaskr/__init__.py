import os

from flask import Flask
import time
import logging
logger = logging.getLogger(__name__)


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    logger.error(">>> Entering create_app(test_config=%s)", test_config, extra={"event.action": "create_app", "logrite.test_config": test_config})
    app = Flask(__name__, instance_relative_config=True)
    logger.error("create_app(test_config=%s): app → %s", test_config, app, extra={"event.action": "create_app", "logrite.test_config": test_config})
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        __log_start = time.time()
        # load the test config if passed in
        app.config.update(test_config)
        logger.error("create_app(test_config)=%s: update operation took %s ms", test_config, int((time.time() - __log_start) * 1000), extra={"event.action": "create_app", "event.category": "database", "logrite.test_config": test_config})

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    @app.route("/hello")
    def hello():
        logger.error(">>> Entering hello()", extra={"event.action": "hello"})
        logger.warning("<<< Exiting hello()", extra={"event.action": "hello"})
        return "Hello, World!"

    # register the database commands
    from . import db

    db.init_app(app)

    # apply the blueprints to the app
    from . import auth
    from . import blog

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule("/", endpoint="index")

    return app
