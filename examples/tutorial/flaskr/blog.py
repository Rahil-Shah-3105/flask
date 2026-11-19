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
import time
import logging
logger = logging.getLogger(__name__)

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    logger.error(">>> Entering index()", extra={"event.action": "index"})
    __log_start = time.time()
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    logger.error("index(): db → %s", db, extra={"event.action": "index"})
    logger.error("index()=: query operation took %s ms", int((time.time() - __log_start) * 1000), extra={"event.action": "index", "event.category": "database"})
    logger.warning("<<< Exiting index()", extra={"event.action": "index"})
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
    logger.error(">>> Entering get_post(id=%s,check_author=%s)", id, check_author, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
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

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    logger.warning("<<< Exiting get_post(id=%s,check_author=%s)", id, check_author, extra={"event.action": "get_post", "logrite.id": id, "logrite.check_author": check_author})
    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    logger.error(">>> Entering create()", extra={"event.action": "create"})
    if request.method == "POST":
        title = request.form["title"]
        logger.error("create(): title → %s", title, extra={"event.action": "create"})
        body = request.form["body"]
        logger.error("create(): body → %s", body, extra={"event.action": "create"})
        error = None
        logger.error("create(): error → %s", error, extra={"event.action": "create"})

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            logger.error("create(): db → %s", db, extra={"event.action": "create"})
            db.execute(
                "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    logger.warning("<<< Exiting create()", extra={"event.action": "create"})
    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    logger.error(">>> Entering update(id=%s)", id, extra={"event.action": "update", "logrite.id": id})
    post = get_post(id)
    logger.error("update(id=%s): post → %s", id, post, extra={"event.action": "update", "logrite.id": id})

    if request.method == "POST":
        title = request.form["title"]
        logger.error("update(id=%s): title → %s", id, title, extra={"event.action": "update", "logrite.id": id})
        body = request.form["body"]
        logger.error("update(id=%s): body → %s", id, body, extra={"event.action": "update", "logrite.id": id})
        error = None
        logger.error("update(id=%s): error → %s", id, error, extra={"event.action": "update", "logrite.id": id})

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            logger.error("update(id=%s): db → %s", id, db, extra={"event.action": "update", "logrite.id": id})
            db.execute(
                "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))

    logger.warning("<<< Exiting update(id=%s)", id, extra={"event.action": "update", "logrite.id": id})
    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    logger.error(">>> Entering delete(id=%s)", id, extra={"event.action": "delete", "logrite.id": id})
    get_post(id)
    db = get_db()
    logger.error("delete(id=%s): db → %s", id, db, extra={"event.action": "delete", "logrite.id": id})
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    logger.warning("<<< Exiting delete(id=%s)", id, extra={"event.action": "delete", "logrite.id": id})
    return redirect(url_for("blog.index"))
