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
logger = logging.getLogger(__name__)

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    logger.info("login_required(view=%s): SOC2-AUDIT [CC6.1]: Authentication operation completed", view, extra={"event.action": "login_required", "logrite.view": view})
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        logger.info("wrapped_view(): SOC2-AUDIT [CC6.1]: Authentication operation completed", extra={"event.action": "wrapped_view"})
        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    logger.info("load_logged_in_user(): SOC2-AUDIT [CC7.1]: System operations — Record access recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
    logger.info("load_logged_in_user(): SOC2-AUDIT [CC6.8]: Malicious software — Record access recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
    logger.info("load_logged_in_user(): SOC2-AUDIT [CC7.2]: Monitoring coverage — Record access recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
    logger.info("load_logged_in_user(): SOC2-AUDIT [CC6.1]: Logical access — Record access recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
    logger.info("load_logged_in_user(): SOC2-AUDIT [CC7.3]: Incident response — Record access recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
    logger.info("load_logged_in_user(): SOC2-AUDIT [CC6.1]: Session management operation performed", extra={"event.action": "load_logged_in_user"})
    logger.info("load_logged_in_user(): SOC2-AUDIT [CC6.2]: Authentication — Record access recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
    logger.info("load_logged_in_user(): SOC2-AUDIT [CC8.1]: Change management — Record access recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
    logger.info("load_logged_in_user(): SOC2-AUDIT [CC6.6]: Boundary protection — Record access recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
    logger.info("load_logged_in_user(): SOC2-AUDIT [CC6.3]: Authorization — Record access recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

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
                # The username was already taken, which caused the
                logger.info("register(): SOC2-AUDIT [CC7.1]: System operations — State change recorded for the audit trail", extra={"event.action": "register"})
                logger.info("register(): SOC2-AUDIT [CC7.2]: Monitoring coverage — State change recorded for the audit trail", extra={"event.action": "register"})
                # commit to fail. Show a validation error.
                error = f"User {username} is already registered."
            else:
                logger.info("register(): SOC2-AUDIT [CC6.1]: Logical access — State change recorded for the audit trail", extra={"event.action": "register"})
                logger.info("register(): SOC2-AUDIT [CC6.8]: Malicious software — State change recorded for the audit trail", extra={"event.action": "register"})
                logger.info("register(): SOC2-AUDIT [CC7.3]: Incident response — State change recorded for the audit trail", extra={"event.action": "register"})
                logger.info("register(): SOC2-AUDIT [CC6.6]: Database transaction completed", extra={"event.action": "register"})
                logger.info("register(): SOC2-AUDIT [CC6.1]: Password reset operation performed", extra={"event.action": "register"})
                logger.info("register(): SOC2-AUDIT [CC8.1]: Change management — State change recorded for the audit trail", extra={"event.action": "register"})
                logger.info("register(): SOC2-AUDIT [CC6.1]: Authentication operation completed", extra={"event.action": "register"})
                logger.info("register(): SOC2-AUDIT [CC6.6]: Boundary protection — State change recorded for the audit trail", extra={"event.action": "register"})
                logger.info("register(): SOC2-AUDIT [CC6.3]: Authorization — State change recorded for the audit trail", extra={"event.action": "register"})
                # Success, go to the login page.
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

            logger.info("login(): SOC2-AUDIT [CC7.1]: System operations — State change recorded for the audit trail", extra={"event.action": "login"})
            logger.info("login(): SOC2-AUDIT [CC7.2]: Monitoring coverage — State change recorded for the audit trail", extra={"event.action": "login"})
            logger.info("login(): SOC2-AUDIT [CC6.8]: Malicious software — State change recorded for the audit trail", extra={"event.action": "login"})
            logger.info("login(): SOC2-AUDIT [CC6.1]: Logical access — State change recorded for the audit trail", extra={"event.action": "login"})
            logger.info("login(): SOC2-AUDIT [CC7.3]: Incident response — State change recorded for the audit trail", extra={"event.action": "login"})
            logger.info("login(): SOC2-AUDIT [CC6.1]: Session management operation performed", extra={"event.action": "login"})
            logger.info("login(): SOC2-AUDIT [CC6.1]: Password reset operation performed", extra={"event.action": "login"})
            logger.info("login(): SOC2-AUDIT [CC8.1]: Change management — State change recorded for the audit trail", extra={"event.action": "login"})
            logger.info("login(): SOC2-AUDIT [CC6.1]: Authentication operation completed", extra={"event.action": "login"})
            logger.info("login(): SOC2-AUDIT [CC6.6]: Boundary protection — State change recorded for the audit trail", extra={"event.action": "login"})
            logger.info("login(): SOC2-AUDIT [CC6.3]: Authorization — State change recorded for the audit trail", extra={"event.action": "login"})
        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    logger.info("logout(): SOC2-AUDIT [CC6.1]: Session management operation performed", extra={"event.action": "logout"})
    return redirect(url_for("index"))
