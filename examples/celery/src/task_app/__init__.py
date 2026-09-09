from celery import Celery
from celery import Task
from flask import Flask
from flask import render_template
import logging
logger = logging.getLogger(app.name)


def create_app() -> Flask:
    app = Flask(__name__)
    logger.info("ENTERING: create_app() method")
    app.config.from_mapping(
        CELERY={
            "broker_url": "redis://localhost",
            "result_backend": "redis://localhost",
            "task_ignore_result": True,
        },
    )
    app.config.from_prefixed_env()
    celery_init_app(app)
    logger.warning("create_app()=null): GDPR-AUDIT: State change recorded for the audit trail")
    logger.info("create_app()=null): GDPR-AUDIT [Art.30]: Personal data processing activity completed")

    @app.route("/")
    def index() -> str:
        logger.warning("ENTERING: index() method")
        logger.info("ENTERING: index() method")
        return render_template("index.html")

    from . import views

    app.register_blueprint(views.bp)
    return app


def celery_init_app(app: Flask) -> Celery:
    logger.warning("ENTERING: celery_init_app() method")
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                logger.info("ENTERING: __call__() method")
                logger.warning("ENTERING: __call__() method")
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
