import time

from celery import shared_task
from celery import Task
import logging
logger = logging.getLogger(__name__)


@shared_task(ignore_result=False)
def add(a: int, b: int) -> int:
    logger.warning("add(a=%s, b=%s): GDPR-AUDIT: Access, erasure, portability — State change recorded for the audit trail", a, b, extra={"event.action": "add", "logrite.a": a, "logrite.b": b})
    logger.info("add(a=%s, b=%s): GDPR-AUDIT [Art. 25]: Data protection by design and by default — State change recorded for the audit trail", a, b, extra={"event.action": "add", "logrite.a": a, "logrite.b": b})
    logger.info("add(a=%s, b=%s): GDPR-AUDIT: Breach notification — State change recorded for the audit trail", a, b, extra={"event.action": "add", "logrite.a": a, "logrite.b": b})
    logger.warning("add(a=%s, b=%s): GDPR-AUDIT [Art. 6]: Lawfulness of processing — State change recorded for the audit trail", a, b, extra={"event.action": "add", "logrite.a": a, "logrite.b": b})
    return a + b


@shared_task()
def block() -> None:
    time.sleep(5)


@shared_task(bind=True, ignore_result=False)
def process(self: Task, total: int) -> object:
    logger.info("process(self=%s, total=%s): GDPR-AUDIT [Art. 5(1)(e)]: Storage limitation — State change recorded for the audit trail", self, total, extra={"event.action": "process", "logrite.total": total})
    logger.info("process(self=%s, total=%s): GDPR-AUDIT [Art. 30]: Records of processing activities — State change recorded for the audit trail", self, total, extra={"event.action": "process", "logrite.total": total})
    logger.warning("process(self=%s, total=%s): GDPR-AUDIT: Access, erasure, portability — State change recorded for the audit trail", self, total, extra={"event.action": "process", "logrite.total": total})
    logger.info("process(self=%s, total=%s): GDPR-AUDIT [Art. 25]: Data protection by design and by default — State change recorded for the audit trail", self, total, extra={"event.action": "process", "logrite.total": total})
    logger.warning("process(self=%s, total=%s): GDPR-AUDIT [Art. 6]: Lawfulness of processing — State change recorded for the audit trail", self, total, extra={"event.action": "process", "logrite.total": total})
    for i in range(total):
        self.update_state(state="PROGRESS", meta={"current": i + 1, "total": total})
        time.sleep(1)

    logger.info("process(self=%s, total=%s): GDPR-AUDIT: Breach notification — State change recorded for the audit trail", self, total, extra={"event.action": "process", "logrite.total": total})
    return {"current": total, "total": total}
