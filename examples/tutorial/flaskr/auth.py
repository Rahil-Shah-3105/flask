import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from .db import get_db
import logging
logger = logging.getLogger(app.name)

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    logger.debug(">>> Entering login_required(view=%s)", view)

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        logger.debug(">>> Entering wrapped_view()")
        if g.user is None:
            return redirect(url_for("auth.login"))

        logger.debug("<<< Exiting wrapped_view()")
        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    logger.debug(">>> Entering load_logged_in_user()")
    logger.debug("load_logged_in_user(): user_id → %s", user_id)
    logger.info("load_logged_in_user()=: find operation took %s ms", int((time.time() - __log_start) * 1000))
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
        logger.debug("load_logged_in_user(): g.user → %s", g.user)
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )
        logger.debug("<<< Exiting load_logged_in_user()")


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    logger.debug(">>> Entering register()")
    logger.debug("register(): password → <redacted>")
    logger.debug("register(): username → %s", username)
    logger.warning("register(): password → %s", password)
    logger.debug("register(): db → %s", db)
    logger.debug("register(): error → %s", error)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

            logger.info("register()=: query operation took %s ms", int((time.time() - __log_start) * 1000))
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                logger.error("Exception in register()", exc_info=True)
                # The username was already taken, which caused the
                # commit to fail. Show a validation error.
                error = f"User {username} is already registered."
            else:
                # Success, go to the login page.
                return redirect(url_for("auth.login"))

        flash(error)

    logger.debug("<<< Exiting register()")
    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    logger.debug(">>> Entering login()")
    logger.debug("login(): db → %s", db)
    logger.debug("login(): password → <redacted>")
    logger.debug("login(): username → %s", username)
    logger.warning("login(): password → %s", password)
    logger.debug("login(): error → %s", error)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        logger.debug("login(): user → %s", user)
        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    logger.debug("<<< Exiting login()")
    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    logger.debug(">>> Entering logout()")
    session.clear()
    logger.debug("<<< Exiting logout()")
    return redirect(url_for("index"))
