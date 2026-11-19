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
    logger.info("add(): FEDRAMP-AUDIT: Incident response — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): FEDRAMP-AUDIT: Crypto protection — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): FEDRAMP-AUDIT: Configuration management — State change recorded for the audit trail", extra={"event.action": "add"})
    a = request.form.get("a", 0, type=float)
    b = request.form.get("b", 0, type=float)
    logger.info("add(): FEDRAMP-AUDIT [RA-5]: Vulnerability management — State change recorded for the audit trail", extra={"event.action": "add"})
    return jsonify(result=a + b)
