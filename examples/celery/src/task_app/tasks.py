import time

from celery import shared_task
from celery import Task
import logging
logger = logging.getLogger(__name__)


@shared_task(ignore_result=False)
def add(a: int, b: int) -> int:
    logger.info("add(a=%s, b=%s): ISO27001-AUDIT: Incident management — State change recorded for the audit trail", a, b, extra={"event.action": "add", "logrite.a": a, "logrite.b": b})
    logger.info("add(a=%s, b=%s): ISO27001-AUDIT [A.8.24]: Cryptography — State change recorded for the audit trail", a, b, extra={"event.action": "add", "logrite.a": a, "logrite.b": b})
    logger.info("add(a=%s, b=%s): ISO27001-AUDIT: Access control — State change recorded for the audit trail", a, b, extra={"event.action": "add", "logrite.a": a, "logrite.b": b})
    logger.info("add(a=%s, b=%s): ISO27001-AUDIT: Continuity — State change recorded for the audit trail", a, b, extra={"event.action": "add", "logrite.a": a, "logrite.b": b})
    return a + b


@shared_task()
def block() -> None:
    time.sleep(5)


@shared_task(bind=True, ignore_result=False)
def process(self: Task, total: int) -> object:
    logger.info("process(self=%s, total=%s): ISO27001-AUDIT: Supplier security — State change recorded for the audit trail", self, total, extra={"event.action": "process", "logrite.total": total})
    logger.info("process(self=%s, total=%s): ISO27001-AUDIT: Logging — State change recorded for the audit trail", self, total, extra={"event.action": "process", "logrite.total": total})
    logger.info("process(self=%s, total=%s): ISO27001-AUDIT: Incident management — State change recorded for the audit trail", self, total, extra={"event.action": "process", "logrite.total": total})
    logger.info("process(self=%s, total=%s): ISO27001-AUDIT [A.8.24]: Cryptography — State change recorded for the audit trail", self, total, extra={"event.action": "process", "logrite.total": total})
    logger.info("process(self=%s, total=%s): ISO27001-AUDIT: Continuity — State change recorded for the audit trail", self, total, extra={"event.action": "process", "logrite.total": total})
    for i in range(total):
        self.update_state(state="PROGRESS", meta={"current": i + 1, "total": total})
        time.sleep(1)

    logger.info("process(self=%s, total=%s): ISO27001-AUDIT: Access control — State change recorded for the audit trail", self, total, extra={"event.action": "process", "logrite.total": total})
    return {"current": total, "total": total}
