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
import time
import logging
logger = logging.getLogger(__name__)

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    logger.error(">>> Entering login_required(view=%s)", view, extra={"event.action": "login_required", "logrite.view": view})

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        logger.error(">>> Entering wrapped_view()", extra={"event.action": "wrapped_view"})
        if g.user is None:
            return redirect(url_for("auth.login"))

        logger.warning("<<< Exiting wrapped_view()", extra={"event.action": "wrapped_view"})
        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    __log_start = time.time()
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    logger.error(">>> Entering load_logged_in_user()", extra={"event.action": "load_logged_in_user"})
    user_id = session.get("user_id")
    logger.error("load_logged_in_user(): user_id → %s", user_id, extra={"event.action": "load_logged_in_user"})
    logger.error("load_logged_in_user()=: find operation took %s ms", int((time.time() - __log_start) * 1000), extra={"event.action": "load_logged_in_user", "event.category": "database"})

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )
        logger.debug("load_logged_in_user(): g.user → %s", g.user, extra={"event.action": "load_logged_in_user"})
        logger.warning("<<< Exiting load_logged_in_user()", extra={"event.action": "load_logged_in_user"})


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    logger.error(">>> Entering register()", extra={"event.action": "register"})
    if request.method == "POST":
        username = request.form["username"]
        logger.error("register(): username → %s", username, extra={"event.action": "register"})
        password = request.form["password"]
        logger.error("register(): password → <redacted>", extra={"event.action": "register"})
        db = get_db()
        logger.error("register(): db → %s", db, extra={"event.action": "register"})
        error = None
        logger.error("register(): error → %s", error, extra={"event.action": "register"})

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                logger.error("Exception in register()", exc_info=True, extra={"event.action": "register", "event.category": "process"})
                # The username was already taken, which caused the
                # commit to fail. Show a validation error.
                error = f"User {username} is already registered."
            else:
                # Success, go to the login page.
                return redirect(url_for("auth.login"))

        flash(error)

    logger.warning("<<< Exiting register()", extra={"event.action": "register"})
    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    logger.error(">>> Entering login()", extra={"event.action": "login"})
    if request.method == "POST":
        username = request.form["username"]
        logger.error("login(): username → %s", username, extra={"event.action": "login"})
        password = request.form["password"]
        logger.error("login(): password → <redacted>", extra={"event.action": "login"})
        db = get_db()
        error = None
        logger.error("login(): db → %s", db, extra={"event.action": "login"})
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()
        logger.error("login(): error → %s", error, extra={"event.action": "login"})

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

    logger.warning("<<< Exiting login()", extra={"event.action": "login"})
    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    logger.error(">>> Entering logout()", extra={"event.action": "logout"})
    session.clear()
    logger.warning("<<< Exiting logout()", extra={"event.action": "logout"})
    return redirect(url_for("index"))
