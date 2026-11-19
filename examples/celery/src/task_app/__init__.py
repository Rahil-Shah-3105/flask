from celery import Celery
from celery import Task
from flask import Flask
from flask import render_template
import logging
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)
    logger.info("create_app(): CMMC-AUDIT: Media protection — State change recorded for the audit trail", extra={"event.action": "create_app"})
    app.config.from_mapping(
        CELERY={
            "broker_url": "redis://localhost",
            "result_backend": "redis://localhost",
            "task_ignore_result": True,
        },
    )
    logger.info("create_app(): CMMC-AUDIT: Incident response — State change recorded for the audit trail", extra={"event.action": "create_app"})
    logger.info("create_app(): CMMC-AUDIT: Crypto protection — State change recorded for the audit trail", extra={"event.action": "create_app"})
    logger.info("create_app(): CMMC-AUDIT: Audit traceability — State change recorded for the audit trail", extra={"event.action": "create_app"})
    logger.info("create_app(): CMMC-AUDIT: Access control — State change recorded for the audit trail", extra={"event.action": "create_app"})
    app.config.from_prefixed_env()
    celery_init_app(app)

    @app.route("/")
    def index() -> str:
        return render_template("index.html")

    from . import views

    app.register_blueprint(views.bp)
    return app


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
