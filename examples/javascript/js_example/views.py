from flask import jsonify
from flask import render_template
from flask import request

from . import app
import logging
logger = logging.getLogger(app.name)


@app.route("/", defaults={"js": "fetch"})
@app.route("/<any(xhr, jquery, fetch):js>")
def index(js):
    logger.debug(">>> Entering index(js=%s)", js)
    logger.debug("<<< Exiting index(js=%s)", js)
    return render_template(f"{js}.html", js=js)


@app.route("/add", methods=["POST"])
def add():
    logger.debug(">>> Entering add()")
    a = request.form.get("a", 0, type=float)
    logger.debug("add(): a → %s", a)
    b = request.form.get("b", 0, type=float)
    logger.debug("add(): b → %s", b)
    logger.debug("<<< Exiting add()")
    return jsonify(result=a + b)
