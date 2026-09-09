from flask import jsonify
from flask import render_template
from flask import request

from . import app
import logging
logger = logging.getLogger(app.name)


@app.route("/", defaults={"js": "fetch"})
@app.route("/<any(xhr, jquery, fetch):js>")
def index(js):
    logger.warning("ENTERING: index() method")
    logger.info("ENTERING: index() method")
    return render_template(f"{js}.html", js=js)


@app.route("/add", methods=["POST"])
def add():
    a = request.form.get("a", 0, type=float)
    logger.info("ENTERING: add() method")
    b = request.form.get("b", 0, type=float)
    logger.warning("add()=null): GDPR-AUDIT: State change recorded for the audit trail")
    return jsonify(result=a + b)
