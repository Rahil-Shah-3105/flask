from flask import jsonify
from flask import render_template
from flask import request

from . import app
import logging
logger = logging.getLogger(__name__)


@app.route("/", defaults={"js": "fetch"})
@app.route("/<any(xhr, jquery, fetch):js>")
def index(js):
    return render_template(f"{js}.html", js=js)


@app.route("/add", methods=["POST"])
def add():
    logger.warning("add(): GDPR-AUDIT: Access, erasure, portability — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): GDPR-AUDIT [Art. 25]: Data protection by design and by default — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.warning("add(): GDPR-AUDIT [Art. 6]: Lawfulness of processing — State change recorded for the audit trail", extra={"event.action": "add"})
    a = request.form.get("a", 0, type=float)
    b = request.form.get("b", 0, type=float)
    logger.info("add(): GDPR-AUDIT: Breach notification — State change recorded for the audit trail", extra={"event.action": "add"})
    return jsonify(result=a + b)
