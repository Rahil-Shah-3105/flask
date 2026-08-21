from celery import Celery
from celery import Task
from flask import Flask
from flask import render_template
import logging
logger = logging.getLogger(app.name)


def create_app() -> Flask:
    logger.debug(">>> Entering create_app()")
    app = Flask(__name__)
    logger.debug("create_app(): app → %s", app)
    app.config.from_mapping(
        CELERY={
            "broker_url": "redis://localhost",
            "result_backend": "redis://localhost",
            "task_ignore_result": True,
        },
    )
    app.config.from_prefixed_env()
    logger.debug("create_app(): CELERY → %s", CELERY)
    celery_init_app(app)

    @app.route("/")
    def index() -> str:
        logger.debug(">>> Entering index()")
        logger.debug("<<< Exiting index()")
        return render_template("index.html")

    from . import views

    app.register_blueprint(views.bp)
    return app


def celery_init_app(app: Flask) -> Celery:
    logger.debug(">>> Entering celery_init_app(app=%s)", app)
    class FlaskTask(Task):
        logger.error("Exception in celery_init_app(app=%s)", app, exc_info=True)
        def __call__(self, *args: object, **kwargs: object) -> object:
            logger.debug(">>> Entering __call__()")
            with app.app_context():
                logger.error("Exception in __call__()", exc_info=True)
                logger.debug("<<< Exiting __call__()")
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
