import time

from celery import shared_task
from celery import Task
import logging
logger = logging.getLogger(__name__)


@shared_task(ignore_result=False)
def add(a: int, b: int) -> int:
    logger.error(">>> Entering add(a=%s,b=%s)", a, b, extra={"event.action": "add", "logrite.a": a, "logrite.b": b})
    logger.warning("<<< Exiting add(a=%s,b=%s)", a, b, extra={"event.action": "add", "logrite.a": a, "logrite.b": b})
    return a + b


@shared_task()
def block() -> None:
    logger.error(">>> Entering block()", extra={"event.action": "block"})
    time.sleep(5)
    logger.warning("<<< Exiting block()", extra={"event.action": "block"})


@shared_task(bind=True, ignore_result=False)
def process(self: Task, total: int) -> object:
    logger.error(">>> Entering process(total=%s)", total, extra={"event.action": "process", "logrite.total": total})
    for i in range(total):
        self.update_state(state="PROGRESS", meta={"current": i + 1, "total": total})
        time.sleep(1)

    logger.warning("<<< Exiting process(total=%s)", total, extra={"event.action": "process", "logrite.total": total})
    return {"current": total, "total": total}
