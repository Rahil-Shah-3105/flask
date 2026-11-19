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
    logger.info("add(): COAI-AUDIT: Impact assessment — State change recorded for the audit trail", extra={"event.action": "add"})
    logger.info("add(): COAI-AUDIT: Consumer notice — State change recorded for the audit trail", extra={"event.action": "add"})
    b = request.form.get("b", 0, type=float)
    logger.info("add(): COAI-AUDIT: Admt adverse — State change recorded for the audit trail", extra={"event.action": "add"})
    return jsonify(result=a + b)
