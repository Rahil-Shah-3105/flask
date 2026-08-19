from celery.result import AsyncResult
from flask import Blueprint
from flask import request

from . import tasks
import logging
logger = logging.getLogger(app.name)

bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@bp.get("/result/<id>")
def result(id: str) -> dict[str, object]:
    logger.debug(">>> Entering result(id=%s)", id)
    result = AsyncResult(id)
    logger.debug("result(id=%s): result → %s", id, result)
    ready = result.ready()
    logger.debug("result(id=%s): ready → %s", id, ready)
    return {
        "ready": ready,
        "successful": result.successful() if ready else None,
        "value": result.get() if ready else result.result,
    }
    logger.debug("<<< Exiting result(id=%s)", id)


@bp.post("/add")
def add() -> dict[str, object]:
    logger.debug(">>> Entering add()")
    a = request.form.get("a", type=int)
    logger.debug("add(): a → %s", a)
    b = request.form.get("b", type=int)
    logger.debug("add(): b → %s", b)
    result = tasks.add.delay(a, b)
    logger.debug("add(): result → %s", result)
    logger.debug("<<< Exiting add()")
    return {"result_id": result.id}


@bp.post("/block")
def block() -> dict[str, object]:
    logger.debug(">>> Entering block()")
    result = tasks.block.delay()
    logger.debug("block(): result → %s", result)
    logger.debug("<<< Exiting block()")
    return {"result_id": result.id}


@bp.post("/process")
def process() -> dict[str, object]:
    logger.debug(">>> Entering process()")
    result = tasks.process.delay(total=request.form.get("total", type=int))
    logger.debug("<<< Exiting process()")
    return {"result_id": result.id}
