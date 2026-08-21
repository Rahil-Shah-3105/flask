import time

from celery import shared_task
from celery import Task
import logging
logger = logging.getLogger(app.name)


@shared_task(ignore_result=False)
def add(a: int, b: int) -> int:
    logger.debug(">>> Entering add(a=%s,b=%s)", a, b)
    logger.debug("<<< Exiting add(a=%s,b=%s)", a, b)
    return a + b


@shared_task()
def block() -> None:
    logger.debug(">>> Entering block()")
    time.sleep(5)
    logger.debug("<<< Exiting block()")


@shared_task(bind=True, ignore_result=False)
def process(self: Task, total: int) -> object:
    logger.debug(">>> Entering process(total=%s)", total)
    for i in range(total):
        self.update_state(state="PROGRESS", meta={"current": i + 1, "total": total})
        time.sleep(1)

    logger.debug("<<< Exiting process(total=%s)", total)
    return {"current": total, "total": total}
