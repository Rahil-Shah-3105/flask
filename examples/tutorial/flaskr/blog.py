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
    logger.info("index(): GDPR-AUDIT [Art. 5(1)(e)]: Storage limitation — State change recorded for the audit trail", extra={"event.action": "index"})
    logger.info("index(): GDPR-AUDIT [Art. 30]: Records of processing activities — State change recorded for the audit trail", extra={"event.action": "index"})
    logger.warning("index(): GDPR-AUDIT: Access, erasure, portability — State change recorded for the audit trail", extra={"event.action": "index"})
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    logger.info("index(): GDPR-AUDIT [Art. 25]: Data protection by design and by default — State change recorded for the audit trail", extra={"event.action": "index"})
    logger.info("index(): GDPR-AUDIT [Art. 32]: Security of processing — State change recorded for the audit trail", extra={"event.action": "index"})
    logger.info("index(): GDPR-AUDIT: Breach notification — State change recorded for the audit trail", extra={"event.action": "index"})
    logger.warning("index(): GDPR-AUDIT [Art. 6]: Lawfulness of processing — State change recorded for the audit trail", extra={"event.action": "index"})
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

    logger.info("get_post(id=%s, check_author=%s): GDPR-AUDIT: Transfers to third countries — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): GDPR-AUDIT [Art. 32]: Security of processing — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): GDPR-AUDIT [Art. 5(1)(e)]: Storage limitation — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): GDPR-AUDIT [Art. 30]: Records of processing activities — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.warning("get_post(id=%s, check_author=%s): GDPR-AUDIT: Access, erasure, portability — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): GDPR-AUDIT [Art. 25]: Data protection by design and by default — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): GDPR-AUDIT [Art.30]: Personal data processing activity completed", id, check_author, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.info("get_post(id=%s, check_author=%s): GDPR-AUDIT: Breach notification — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    logger.warning("get_post(id=%s, check_author=%s): GDPR-AUDIT [Art. 6]: Lawfulness of processing — Record access recorded for the audit trail %s", id, check_author, id, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
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
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            logger.info("create(): GDPR-AUDIT: Transfers to third countries — State change recorded for the audit trail", extra={"event.action": "create"})
            logger.info("create(): GDPR-AUDIT [Art. 32]: Security of processing — State change recorded for the audit trail", extra={"event.action": "create"})
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            logger.info("create(): GDPR-AUDIT [Art. 5(1)(e)]: Storage limitation — State change recorded for the audit trail", extra={"event.action": "create"})
            logger.info("create(): GDPR-AUDIT [Art. 30]: Records of processing activities — State change recorded for the audit trail", extra={"event.action": "create"})
            logger.warning("create(): GDPR-AUDIT: Access, erasure, portability — State change recorded for the audit trail", extra={"event.action": "create"})
            logger.info("create(): GDPR-AUDIT [Art. 25]: Data protection by design and by default — State change recorded for the audit trail", extra={"event.action": "create"})
            logger.info("create(): GDPR-AUDIT: Breach notification — State change recorded for the audit trail", extra={"event.action": "create"})
            logger.warning("create(): GDPR-AUDIT [Art. 6]: Lawfulness of processing — State change recorded for the audit trail", extra={"event.action": "create"})
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
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            logger.info("update(id=%s): GDPR-AUDIT: Transfers to third countries — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
            logger.info("update(id=%s): GDPR-AUDIT [Art. 32]: Security of processing — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, id)
            )
            logger.info("update(id=%s): GDPR-AUDIT [Art. 5(1)(e)]: Storage limitation — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
            logger.info("update(id=%s): GDPR-AUDIT [Art. 30]: Records of processing activities — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
            logger.warning("update(id=%s): GDPR-AUDIT [Art.15]: Data subject right exercised for data subject %s", id, id, extra={"event.action": "update", "logrite.id": id})
            logger.info("update(id=%s): GDPR-AUDIT [Art. 25]: Data protection by design and by default — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
            logger.info("update(id=%s): GDPR-AUDIT: Breach notification — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
            logger.warning("update(id=%s): GDPR-AUDIT [Art. 6]: Lawfulness of processing — State change recorded for the audit trail %s", id, id, extra={"event.action": "update", "logrite.id": id})
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
    logger.info("delete(id=%s): GDPR-AUDIT [Art. 5(1)(e)]: Storage limitation — State change recorded for the audit trail %s", id, id, extra={"event.action": "delete", "logrite.id": id})
    logger.info("delete(id=%s): GDPR-AUDIT [Art. 32]: Security of processing — State change recorded for the audit trail %s", id, id, extra={"event.action": "delete", "logrite.id": id})
    logger.info("delete(id=%s): GDPR-AUDIT: Transfers to third countries — State change recorded for the audit trail %s", id, id, extra={"event.action": "delete", "logrite.id": id})
    logger.info("delete(id=%s): GDPR-AUDIT [Art. 30]: Records of processing activities — State change recorded for the audit trail %s", id, id, extra={"event.action": "delete", "logrite.id": id})
    logger.warning("delete(id=%s): GDPR-AUDIT [Art.17]: Data subject right exercised — erasure/portability request processed %s", id, id, extra={"event.action": "delete", "logrite.id": id})
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    logger.info("delete(id=%s): GDPR-AUDIT: Breach notification — State change recorded for the audit trail %s", id, id, extra={"event.action": "delete", "logrite.id": id})
    return redirect(url_for("blog.index"))
