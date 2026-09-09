from celery.result import AsyncResult
from flask import Blueprint
from flask import request

from . import tasks
import logging
logger = logging.getLogger(app.name)

bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@bp.get("/result/<id>")
def result(id: str) -> dict[str, object]:
    result = AsyncResult(id)
    logger.info("ENTERING: result() method")
    ready = result.ready()
    return {
        "ready": ready,
        "successful": result.successful() if ready else None,
        "value": result.get() if ready else result.result,
    }


@bp.post("/add")
def add() -> dict[str, object]:
    a = request.form.get("a", type=int)
    logger.info("ENTERING: add() method")
    logger.warning("add()=null): GDPR-AUDIT: State change recorded for the audit trail")
    b = request.form.get("b", type=int)
    result = tasks.add.delay(a, b)
    return {"result_id": result.id}


@bp.post("/block")
def block() -> dict[str, object]:
    result = tasks.block.delay()
    logger.info("ENTERING: block() method")
    logger.warning("ENTERING: block() method")
    return {"result_id": result.id}


@bp.post("/process")
def process() -> dict[str, object]:
    result = tasks.process.delay(total=request.form.get("total", type=int))
    logger.info("ENTERING: process() method")
    logger.warning("ENTERING: process() method")
    logger.warning("process()=null): GDPR-AUDIT: State change recorded for the audit trail")
    return {"result_id": result.id}
