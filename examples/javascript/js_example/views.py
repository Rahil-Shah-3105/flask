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
    logger.info("add(): SOX-AUDIT: Access to programs and data — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): SOX-AUDIT: Change management (PCAOB AS 2201) — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): SOX-AUDIT: Computer operations — State change recorded for the audit trail", extra={"event.action": "add"})
    a = request.form.get("a", 0, type=float)
    b = request.form.get("b", 0, type=float)
    logger.info("add(): SOX-AUDIT: Privileged access — State change recorded for the audit trail", extra={"event.action": "add"})
    return jsonify(result=a + b)
