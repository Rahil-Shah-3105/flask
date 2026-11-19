from celery import Celery
from celery import Task
from flask import Flask
from flask import render_template
import logging
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    logger.error(">>> Entering create_app()", extra={"event.action": "create_app"})
    app = Flask(__name__)
    logger.error("create_app(): app → %s", app, extra={"event.action": "create_app"})
    app.config.from_mapping(
        CELERY={
            "broker_url": "redis://localhost",
            "result_backend": "redis://localhost",
            "task_ignore_result": True,
        },
    )
    app.config.from_prefixed_env()
    celery_init_app(app)

    @app.route("/")
    def index() -> str:
        logger.error(">>> Entering index()", extra={"event.action": "index"})
        logger.warning("<<< Exiting index()", extra={"event.action": "index"})
        return render_template("index.html")

    from . import views

    app.register_blueprint(views.bp)
    return app


def celery_init_app(app: Flask) -> Celery:
    logger.error(">>> Entering celery_init_app(app=%s)", app, extra={"event.action": "celery_init_app", "logrite.app": app})
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            logger.error(">>> Entering __call__()", extra={"event.action": "__call__"})
            with app.app_context():
                logger.warning("<<< Exiting __call__()", extra={"event.action": "__call__"})
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
