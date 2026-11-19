from celery.result import AsyncResult
from flask import Blueprint
from flask import request

from . import tasks
import time
import logging
logger = logging.getLogger(__name__)

bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@bp.get("/result/<id>")
def result(id: str) -> dict[str, object]:
    logger.error(">>> Entering result(id=%s)", id, extra={"event.action": "result", "logrite.id": id})
    result = AsyncResult(id)
    logger.error("result(id=%s): result → %s", id, result, extra={"event.action": "result", "logrite.id": id})
    ready = result.ready()
    logger.error("result(id=%s): ready → %s", id, ready, extra={"event.action": "result", "logrite.id": id})
    return {
        "ready": ready,
        "successful": result.successful() if ready else None,
        "value": result.get() if ready else result.result,
    }
    logger.warning("<<< Exiting result(id=%s)", id, extra={"event.action": "result", "logrite.id": id})


@bp.post("/add")
def add() -> dict[str, object]:
    logger.error(">>> Entering add()", extra={"event.action": "add"})
    __log_start = time.time()
    a = request.form.get("a", type=int)
    b = request.form.get("b", type=int)
    logger.error("add(): a → %s", a, extra={"event.action": "add"})
    logger.error("add(): b → %s", b, extra={"event.action": "add"})
    logger.error("add()=: external service call took %s ms", int((time.time() - __log_start) * 1000), extra={"event.action": "add", "event.category": "network"})
    result = tasks.add.delay(a, b)
    logger.warning("<<< Exiting add()", extra={"event.action": "add"})
    logger.error("add(): result → %s", result, extra={"event.action": "add"})
    return {"result_id": result.id}


@bp.post("/block")
def block() -> dict[str, object]:
    logger.error(">>> Entering block()", extra={"event.action": "block"})
    __log_start = time.time()
    result = tasks.block.delay()
    logger.error("block(): result → %s", result, extra={"event.action": "block"})
    logger.error("block()=: external service call took %s ms", int((time.time() - __log_start) * 1000), extra={"event.action": "block", "event.category": "network"})
    logger.warning("<<< Exiting block()", extra={"event.action": "block"})
    return {"result_id": result.id}


@bp.post("/process")
def process() -> dict[str, object]:
    logger.error(">>> Entering process()", extra={"event.action": "process"})
    __log_start = time.time()
    result = tasks.process.delay(total=request.form.get("total", type=int))
    logger.error("process(): result → %s", result, extra={"event.action": "process"})
    logger.warning("<<< Exiting process()", extra={"event.action": "process"})
    return {"result_id": result.id}
