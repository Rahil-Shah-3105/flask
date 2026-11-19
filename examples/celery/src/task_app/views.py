from celery.result import AsyncResult
from flask import Blueprint
from flask import request

from . import tasks
import logging
logger = logging.getLogger(__name__)

bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@bp.get("/result/<id>")
def result(id: str) -> dict[str, object]:
    result = AsyncResult(id)
    ready = result.ready()
    return {
        "ready": ready,
        "successful": result.successful() if ready else None,
        "value": result.get() if ready else result.result,
    }


@bp.post("/add")
def add() -> dict[str, object]:
    a = request.form.get("a", type=int)
    logger.info("add(): CMMC-AUDIT: Media protection — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): CMMC-AUDIT: Incident response — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): CMMC-AUDIT: Access control — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): CMMC-AUDIT: Crypto protection — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): CMMC-AUDIT: Audit traceability — State change recorded for the audit trail", extra={"event.action": "add"})
    b = request.form.get("b", type=int)
    result = tasks.add.delay(a, b)
    return {"result_id": result.id}


@bp.post("/block")
def block() -> dict[str, object]:
    result = tasks.block.delay()
    return {"result_id": result.id}


@bp.post("/process")
def process() -> dict[str, object]:
    logger.info("process(): CMMC-AUDIT: Crypto protection — State change recorded for the audit trail", extra={"event.action": "process"})
    logger.info("process(): CMMC-AUDIT: Audit traceability — State change recorded for the audit trail", extra={"event.action": "process"})
    result = tasks.process.delay(total=request.form.get("total", type=int))
    logger.info("process(): CMMC-AUDIT: Incident response — State change recorded for the audit trail", extra={"event.action": "process"})
    return {"result_id": result.id}
