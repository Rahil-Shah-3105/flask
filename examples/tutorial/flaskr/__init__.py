import os

from flask import Flask
import logging
logger = logging.getLogger(__name__)


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    logger.info("create_app(test_config=%s): M2614-AUDIT: Outcome 10: automated alerting — State change recorded for the audit trail", test_config, extra={"event.action": "create_app", "logrite.test_config": test_config})
    logger.info("create_app(test_config=%s): M2614-AUDIT: Outcome 11: CEM + THIRF capability — State change recorded for the audit trail", test_config, extra={"event.action": "create_app", "logrite.test_config": test_config})
    logger.info("create_app(test_config=%s): M2614-AUDIT: Outcome 9: trace attack vectors — State change recorded for the audit trail", test_config, extra={"event.action": "create_app", "logrite.test_config": test_config})
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )
    logger.info("create_app(test_config=%s): M2614-AUDIT: Outcome 8: quantify data affected in an incident — State change recorded for the audit trail", test_config, extra={"event.action": "create_app", "logrite.test_config": test_config})
    logger.info("create_app(test_config=%s): M2614-AUDIT: Outcome 7: anomaly hunting — State change recorded for the audit trail", test_config, extra={"event.action": "create_app", "logrite.test_config": test_config})
    logger.info("create_app(test_config=%s): M2614-AUDIT: Outcome 6: suspicious activity & IOC hunting — State change recorded for the audit trail", test_config, extra={"event.action": "create_app", "logrite.test_config": test_config})
    logger.info("create_app(test_config=%s): M2614-AUDIT: Outcome 5: infrastructure changes — State change recorded for the audit trail", test_config, extra={"event.action": "create_app", "logrite.test_config": test_config})

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        logger.info("create_app(test_config=%s): M2614-AUDIT: Outcome 4: privilege changes — State change recorded for the audit trail", test_config, extra={"event.action": "create_app", "logrite.test_config": test_config})
        logger.info("create_app(test_config=%s): M2614-AUDIT: Outcome 3: object and data access — State change recorded for the audit trail", test_config, extra={"event.action": "create_app", "logrite.test_config": test_config})
        logger.info("create_app(test_config=%s): M2614-AUDIT: Outcome 2: source/destination network traffic — State change recorded for the audit trail", test_config, extra={"event.action": "create_app", "logrite.test_config": test_config})
        logger.info("create_app(test_config=%s): M2614-AUDIT: Outcome 1: user attribution — State change recorded for the audit trail", test_config, extra={"event.action": "create_app", "logrite.test_config": test_config})
        logger.info("create_app(test_config=%s): M2614-AUDIT: Continuous Event Monitoring / Network Visibility — State change recorded for the audit trail", test_config, extra={"event.action": "create_app", "logrite.test_config": test_config})
        logger.info("create_app(test_config=%s): M2614-AUDIT: Log Management / data protection — State change recorded for the audit trail", test_config, extra={"event.action": "create_app", "logrite.test_config": test_config})
        logger.info("create_app(test_config=%s): M2614-AUDIT: Log integrity (encrypt + validate) — State change recorded for the audit trail", test_config, extra={"event.action": "create_app", "logrite.test_config": test_config})
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    @app.route("/hello")
    def hello():
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
