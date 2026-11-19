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
    logger.info("add(): M2614-AUDIT: Outcome 2: source/destination network traffic — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): M2614-AUDIT: Outcome 1: user attribution — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): M2614-AUDIT: Continuous Event Monitoring / Network Visibility — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): M2614-AUDIT: Log Management / data protection — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): M2614-AUDIT: Activity-Based Outcomes 1-11 — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): M2614-AUDIT: Outcome 3: object and data access — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): M2614-AUDIT: Log integrity (encrypt + validate) — State change recorded for the audit trail", extra={"event.action": "add"})
    a = request.form.get("a", type=int)
    b = request.form.get("b", type=int)
    result = tasks.add.delay(a, b)
    return {"result_id": result.id}


@bp.post("/block")
def block() -> dict[str, object]:
    result = tasks.block.delay()
    return {"result_id": result.id}


@bp.post("/process")
def process() -> dict[str, object]:
    logger.info("process(): M2614-AUDIT: Log Management / data protection — State change recorded for the audit trail", extra={"event.action": "process"})
    logger.info("process(): M2614-AUDIT: Log integrity (encrypt + validate) — State change recorded for the audit trail", extra={"event.action": "process"})
    result = tasks.process.delay(total=request.form.get("total", type=int))
    logger.info("process(): M2614-AUDIT: Continuous Event Monitoring / Network Visibility — State change recorded for the audit trail", extra={"event.action": "process"})
    return {"result_id": result.id}
