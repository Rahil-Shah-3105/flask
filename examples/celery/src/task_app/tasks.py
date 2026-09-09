import time

from celery import shared_task
from celery import Task
import logging
logger = logging.getLogger(app.name)


@shared_task(ignore_result=False)
def add(a: int, b: int) -> int:
    logger.warning("add(a,b)=%s,%s: M2614-AUDIT: State change recorded for the audit trail", a, b)
    return a + b


@shared_task()
def block() -> None:
    time.sleep(5)


@shared_task(bind=True, ignore_result=False)
def process(self: Task, total: int) -> object:
    for i in range(total):
        self.update_state(state="PROGRESS", meta={"current": i + 1, "total": total})
        time.sleep(1)

        logger.warning("process(self,total)=%s,%s: M2614-AUDIT: State change recorded for the audit trail", self, total)
    return {"current": total, "total": total}
