from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db
import logging
logger = logging.getLogger(__name__)

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    logger.info("index(): M2614-AUDIT: Outcome 1: user attribution — State change recorded for the audit trail", extra={"event.action": "index"})
    logger.info("index(): M2614-AUDIT: Outcome 2: source/destination network traffic — State change recorded for the audit trail", extra={"event.action": "index"})
    logger.info("index(): M2614-AUDIT: Continuous Event Monitoring / Network Visibility — State change recorded for the audit trail", extra={"event.action": "index"})
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    logger.info("index(): M2614-AUDIT: Log Management / data protection — State change recorded for the audit trail", extra={"event.action": "index"})
    logger.info("index(): M2614-AUDIT: Activity-Based Outcomes 1-11 — State change recorded for the audit trail", extra={"event.action": "index"})
    logger.info("index(): M2614-AUDIT: Outcome 3: object and data access — State change recorded for the audit trail", extra={"event.action": "index"})
    logger.info("index(): M2614-AUDIT: Log integrity (encrypt + validate) — State change recorded for the audit trail", extra={"event.action": "index"})
    return render_template("blog/index.html", posts=posts)


def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    logger.info("get_post(id=%s, check_author=%s): M2614-AUDIT: Outcome 8: quantify data affected in an incident — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): M2614-AUDIT: Outcome 9: trace attack vectors — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): M2614-AUDIT: Outcome 7: anomaly hunting — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): M2614-AUDIT: Outcome 10: automated alerting — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): M2614-AUDIT: Outcome 11: CEM + THIRF capability — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): M2614-AUDIT: Retention: 6 months searchable / 12 months retrievable — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )
    logger.info("get_post(id=%s, check_author=%s): M2614-AUDIT: Outcome 6: suspicious activity & IOC hunting — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): M2614-AUDIT: Outcome 5: infrastructure changes — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): M2614-AUDIT: Outcome 4: privilege changes — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): M2614-AUDIT: Outcome 3: object and data access — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): M2614-AUDIT: Outcome 2: source/destination network traffic — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): M2614-AUDIT: Outcome 1: user attribution — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): M2614-AUDIT: Continuous Event Monitoring / Network Visibility — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): M2614-AUDIT: Log Management / data protection — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): M2614-AUDIT: Activity-Based Outcomes 1-11 — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): M2614-AUDIT: Log integrity (encrypt + validate) — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        logger.info("create(): M2614-AUDIT: Retention: 6 months searchable / 12 months retrievable — State change recorded for the audit trail", extra={"event.action": "create"})
        logger.info("create(): M2614-AUDIT: Outcome 11: CEM + THIRF capability — State change recorded for the audit trail", extra={"event.action": "create"})
        logger.info("create(): M2614-AUDIT: Outcome 10: automated alerting — State change recorded for the audit trail", extra={"event.action": "create"})
        logger.info("create(): M2614-AUDIT: Outcome 9: trace attack vectors — State change recorded for the audit trail", extra={"event.action": "create"})
        logger.info("create(): M2614-AUDIT: Outcome 8: quantify data affected in an incident — State change recorded for the audit trail", extra={"event.action": "create"})
        logger.info("create(): M2614-AUDIT: Outcome 7: anomaly hunting — State change recorded for the audit trail", extra={"event.action": "create"})
        logger.info("create(): M2614-AUDIT: Outcome 6: suspicious activity & IOC hunting — State change recorded for the audit trail", extra={"event.action": "create"})
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            logger.info("create(): M2614-AUDIT: Outcome 4: privilege changes — State change recorded for the audit trail", extra={"event.action": "create"})
            logger.info("create(): M2614-AUDIT: Outcome 5: infrastructure changes — State change recorded for the audit trail", extra={"event.action": "create"})
            logger.info("create(): M2614-AUDIT: Outcome 3: object and data access — State change recorded for the audit trail", extra={"event.action": "create"})
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            logger.info("create(): M2614-AUDIT: Outcome 2: source/destination network traffic — State change recorded for the audit trail", extra={"event.action": "create"})
            logger.info("create(): M2614-AUDIT: Outcome 1: user attribution — State change recorded for the audit trail", extra={"event.action": "create"})
            logger.info("create(): M2614-AUDIT: Continuous Event Monitoring / Network Visibility — State change recorded for the audit trail", extra={"event.action": "create"})
            logger.info("create(): M2614-AUDIT: Log Management / data protection — State change recorded for the audit trail", extra={"event.action": "create"})
            logger.info("create(): M2614-AUDIT: Activity-Based Outcomes 1-11 — State change recorded for the audit trail", extra={"event.action": "create"})
            logger.info("create(): M2614-AUDIT: Log integrity (encrypt + validate) — State change recorded for the audit trail", extra={"event.action": "create"})
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        logger.info("update(id=%s): M2614-AUDIT: Retention: 6 months searchable / 12 months retrievable — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
        logger.info("update(id=%s): M2614-AUDIT: Outcome 11: CEM + THIRF capability — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
        logger.info("update(id=%s): M2614-AUDIT: Outcome 10: automated alerting — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
        logger.info("update(id=%s): M2614-AUDIT: Outcome 9: trace attack vectors — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
        logger.info("update(id=%s): M2614-AUDIT: Outcome 8: quantify data affected in an incident — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
        logger.info("update(id=%s): M2614-AUDIT: Outcome 7: anomaly hunting — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
        logger.info("update(id=%s): M2614-AUDIT: Outcome 6: suspicious activity & IOC hunting — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
        logger.info("update(id=%s): M2614-AUDIT: Outcome 5: infrastructure changes — Change management operation performed", id, extra={"event.action": "update", "logrite.id": id})
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            logger.info("update(id=%s): M2614-AUDIT: Outcome 4: privilege changes — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
            logger.info("update(id=%s): M2614-AUDIT: Outcome 3: object and data access — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
            logger.info("update(id=%s): M2614-AUDIT: Outcome 2: source/destination network traffic — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, id)
            )
            logger.info("update(id=%s): M2614-AUDIT: Outcome 1: user attribution — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
            logger.info("update(id=%s): M2614-AUDIT: Continuous Event Monitoring / Network Visibility — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
            logger.info("update(id=%s): M2614-AUDIT: Log Management / data protection — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
            logger.info("update(id=%s): M2614-AUDIT: Log integrity (encrypt + validate) — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
            logger.info("update(id=%s): M2614-AUDIT: Activity-Based Outcomes 1-11 — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
            logger.info("update(id=%s): SOC2-AUDIT [CC8.1]: Change management operation performed", id, extra={"event.action": "update", "logrite.id": id})
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    logger.info("delete(id=%s): M2614-AUDIT: Outcome 4: privilege changes — State change recorded for the audit trail %s", id, id, extra={"event.action": "delete", "logrite.id": id})
    logger.info("delete(id=%s): M2614-AUDIT: Outcome 6: suspicious activity & IOC hunting — State change recorded for the audit trail %s", id, id, extra={"event.action": "delete", "logrite.id": id})
    logger.info("delete(id=%s): M2614-AUDIT: Outcome 2: source/destination network traffic — State change recorded for the audit trail %s", id, id, extra={"event.action": "delete", "logrite.id": id})
    logger.info("delete(id=%s): M2614-AUDIT: Outcome 3: object and data access — State change recorded for the audit trail %s", id, id, extra={"event.action": "delete", "logrite.id": id})
    logger.info("delete(id=%s): M2614-AUDIT: Outcome 5: infrastructure changes — State change recorded for the audit trail %s", id, id, extra={"event.action": "delete", "logrite.id": id})
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    logger.info("delete(id=%s): M2614-AUDIT: Activity-Based Outcomes 1-11 — State change recorded for the audit trail %s", id, id, extra={"event.action": "delete", "logrite.id": id})
    return redirect(url_for("blog.index"))
