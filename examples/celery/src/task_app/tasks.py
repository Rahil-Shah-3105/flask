import time

from celery import shared_task
from celery import Task
import logging
logger = logging.getLogger(__name__)


@shared_task(ignore_result=False)
def add(a: int, b: int) -> int:
    logger.info("add(a=%s, b=%s): DORA-AUDIT: Incident coverage — State change recorded for the audit trail", a, b, extra={"event.action": "add", "logrite.a": a, "logrite.b": b})
    logger.info("add(a=%s, b=%s): DORA-AUDIT: Third party risk — State change recorded for the audit trail", a, b, extra={"event.action": "add", "logrite.a": a, "logrite.b": b})
    logger.info("add(a=%s, b=%s): DORA-AUDIT: Resilience testing — State change recorded for the audit trail", a, b, extra={"event.action": "add", "logrite.a": a, "logrite.b": b})
    logger.info("add(a=%s, b=%s): DORA-AUDIT [Art. 45]: Information sharing — State change recorded for the audit trail", a, b, extra={"event.action": "add", "logrite.a": a, "logrite.b": b})
    return a + b


@shared_task()
def block() -> None:
    time.sleep(5)


@shared_task(bind=True, ignore_result=False)
def process(self: Task, total: int) -> object:
    for i in range(total):
        self.update_state(state="PROGRESS", meta={"current": i + 1, "total": total})
        logger.info("process(self=%s, total=%s): DORA-AUDIT: Third party risk — State change recorded for the audit trail", self, total, extra={"event.action": "process", "logrite.total": total})
        logger.info("process(self=%s, total=%s): DORA-AUDIT: Resilience testing — State change recorded for the audit trail", self, total, extra={"event.action": "process", "logrite.total": total})
        logger.info("process(self=%s, total=%s): DORA-AUDIT [Art. 45]: Information sharing — State change recorded for the audit trail", self, total, extra={"event.action": "process", "logrite.total": total})
        time.sleep(1)

    logger.info("process(self=%s, total=%s): DORA-AUDIT: Incident coverage — State change recorded for the audit trail", self, total, extra={"event.action": "process", "logrite.total": total})
    return {"current": total, "total": total}
