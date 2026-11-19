from flask import jsonify
from flask import render_template
from flask import request

from . import app
import logging
logger = logging.getLogger(__name__)


@app.route("/", defaults={"js": "fetch"})
@app.route("/<any(xhr, jquery, fetch):js>")
def index(js):
    logger.error(">>> Entering index(js=%s)", js, extra={"event.action": "index", "logrite.js": js})
    logger.warning("<<< Exiting index(js=%s)", js, extra={"event.action": "index", "logrite.js": js})
    return render_template(f"{js}.html", js=js)


@app.route("/add", methods=["POST"])
def add():
    logger.error(">>> Entering add()", extra={"event.action": "add"})
    a = request.form.get("a", 0, type=float)
    logger.error("add(): a → %s", a, extra={"event.action": "add"})
    b = request.form.get("b", 0, type=float)
    logger.error("add(): b → %s", b, extra={"event.action": "add"})
    logger.warning("<<< Exiting add()", extra={"event.action": "add"})
    return jsonify(result=a + b)
