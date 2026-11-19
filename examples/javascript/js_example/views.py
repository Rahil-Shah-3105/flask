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
    a = request.form.get("a", 0, type=float)
    logger.info("add(): COPPA-AUDIT [16 CFR 312.5]: Vpc coverage — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): COPPA-AUDIT [16 CFR 312.5(a)(2)]: Third party disclosure — State change recorded for the audit trail", extra={"event.action": "add"})
    b = request.form.get("b", 0, type=float)
    logger.info("add(): COPPA-AUDIT [16 CFR 312.10]: Retention deletion — State change recorded for the audit trail", extra={"event.action": "add"})
    return jsonify(result=a + b)
