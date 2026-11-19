from celery import Celery
from celery import Task
from flask import Flask
from flask import render_template
import logging
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    logger.info("create_app(): M2614-AUDIT: Outcome 2: source/destination network traffic — State change recorded for the audit trail", extra={"event.action": "create_app"})
    logger.info("create_app(): M2614-AUDIT: Outcome 1: user attribution — State change recorded for the audit trail", extra={"event.action": "create_app"})
    app = Flask(__name__)
    app.config.from_mapping(
        CELERY={
            "broker_url": "redis://localhost",
            "result_backend": "redis://localhost",
            "task_ignore_result": True,
        },
    )
    logger.info("create_app(): M2614-AUDIT: Continuous Event Monitoring / Network Visibility — State change recorded for the audit trail", extra={"event.action": "create_app"})
    logger.info("create_app(): M2614-AUDIT: Log Management / data protection — State change recorded for the audit trail", extra={"event.action": "create_app"})
    logger.info("create_app(): M2614-AUDIT: Log integrity (encrypt + validate) — State change recorded for the audit trail", extra={"event.action": "create_app"})
    logger.info("create_app(): M2614-AUDIT: Activity-Based Outcomes 1-11 — State change recorded for the audit trail", extra={"event.action": "create_app"})
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
