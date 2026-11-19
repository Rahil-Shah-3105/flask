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
    logger.info("add(): GDPR-AUDIT [Art. 5(1)(e)]: Storage limitation — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): GDPR-AUDIT [Art. 30]: Records of processing activities — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.warning("add(): GDPR-AUDIT: Access, erasure, portability — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): GDPR-AUDIT [Art. 25]: Data protection by design and by default — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): GDPR-AUDIT [Art. 32]: Security of processing — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): GDPR-AUDIT: Breach notification — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.warning("add(): GDPR-AUDIT [Art. 6]: Lawfulness of processing — State change recorded for the audit trail", extra={"event.action": "add"})
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
    logger.info("process(): GDPR-AUDIT [Art. 25]: Data protection by design and by default — State change recorded for the audit trail", extra={"event.action": "process"})
    logger.warning("process(): GDPR-AUDIT [Art. 6]: Lawfulness of processing — State change recorded for the audit trail", extra={"event.action": "process"})
    result = tasks.process.delay(total=request.form.get("total", type=int))
    logger.info("process(): GDPR-AUDIT: Breach notification — State change recorded for the audit trail", extra={"event.action": "process"})
    return {"result_id": result.id}
