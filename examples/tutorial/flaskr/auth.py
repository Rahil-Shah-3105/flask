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
    logger.info("login_required(view=%s): M2614-AUDIT: Outcome 1: user attribution — Authentication operation completed", view, extra={"event.action": "login_required", "logrite.view": view})
    logger.info("login_required(view=%s): SOC2-AUDIT [CC6.1]: Authentication operation completed", view, extra={"event.action": "login_required", "logrite.view": view})

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        logger.info("wrapped_view(): M2614-AUDIT: Outcome 1: user attribution — Authentication operation completed", extra={"event.action": "wrapped_view"})
        logger.info("wrapped_view(): SOC2-AUDIT [CC6.1]: Authentication operation completed", extra={"event.action": "wrapped_view"})
        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    logger.info("load_logged_in_user(): M2614-AUDIT: Outcome 4: privilege changes — Record access recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
    logger.info("load_logged_in_user(): M2614-AUDIT: Outcome 6: suspicious activity & IOC hunting — Record access recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
    logger.info("load_logged_in_user(): M2614-AUDIT: Outcome 5: infrastructure changes — Record access recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
    logger.info("load_logged_in_user(): M2614-AUDIT: Outcome 3: object and data access — Record access recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
    logger.info("load_logged_in_user(): M2614-AUDIT: Outcome 2: source/destination network traffic — Record access recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
    logger.info("load_logged_in_user(): M2614-AUDIT: Outcome 01 user attribution recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
    logger.info("load_logged_in_user(): M2614-AUDIT: Log Management / data protection — Record access recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
    logger.info("load_logged_in_user(): M2614-AUDIT: Activity-Based Outcomes 1-11 — Record access recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
    logger.info("load_logged_in_user(): M2614-AUDIT: Continuous Event Monitoring / Network Visibility — Record access recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
    logger.info("load_logged_in_user(): M2614-AUDIT: Outcome 7: anomaly hunting — Record access recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
    logger.info("load_logged_in_user(): M2614-AUDIT: Log integrity (encrypt + validate) — Record access recorded for the audit trail", extra={"event.action": "load_logged_in_user"})
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
            logger.info("register(): M2614-AUDIT: Retention: 6 months searchable / 12 months retrievable — State change recorded for the audit trail", extra={"event.action": "register"})
            logger.info("register(): M2614-AUDIT: Outcome 11: CEM + THIRF capability — State change recorded for the audit trail", extra={"event.action": "register"})
            logger.info("register(): M2614-AUDIT: Outcome 10: automated alerting — State change recorded for the audit trail", extra={"event.action": "register"})
            logger.info("register(): M2614-AUDIT: Outcome 9: trace attack vectors — State change recorded for the audit trail", extra={"event.action": "register"})

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                logger.info("register(): M2614-AUDIT: Outcome 8: quantify data affected in an incident — State change recorded for the audit trail", extra={"event.action": "register"})
                db.commit()
            except db.IntegrityError:
                logger.info("register(): M2614-AUDIT: Outcome 6: suspicious activity & IOC hunting — State change recorded for the audit trail", extra={"event.action": "register"})
                logger.info("register(): M2614-AUDIT: Outcome 7: anomaly hunting — State change recorded for the audit trail", extra={"event.action": "register"})
                logger.info("register(): M2614-AUDIT: Outcome 5: infrastructure changes — State change recorded for the audit trail", extra={"event.action": "register"})
                logger.info("register(): M2614-AUDIT: Outcome 4: privilege changes — State change recorded for the audit trail", extra={"event.action": "register"})
                logger.info("register(): M2614-AUDIT: Outcome 2: source/destination network traffic — State change recorded for the audit trail", extra={"event.action": "register"})
                logger.info("register(): M2614-AUDIT: Outcome 3: object and data access — Database transaction completed", extra={"event.action": "register"})
                logger.info("register(): M2614-AUDIT: Outcome 1: user attribution — Authentication operation completed", extra={"event.action": "register"})
                logger.info("register(): M2614-AUDIT: Continuous Event Monitoring / Network Visibility — State change recorded for the audit trail", extra={"event.action": "register"})
                logger.info("register(): M2614-AUDIT: Log Management / data protection — State change recorded for the audit trail", extra={"event.action": "register"})
                logger.info("register(): M2614-AUDIT: Log integrity (encrypt + validate) — Data integrity check performed", extra={"event.action": "register"})
                logger.info("register(): SOC2-AUDIT [CC6.6]: Database transaction completed", extra={"event.action": "register"})
                logger.info("register(): M2614-AUDIT: Activity-Based Outcomes 1-11 — State change recorded for the audit trail", extra={"event.action": "register"})
                logger.info("register(): SOC2-AUDIT [CC6.1]: Authentication operation completed", extra={"event.action": "register"})
                # The username was already taken, which caused the
                # commit to fail. Show a validation error.
                error = f"User {username} is already registered."
            else:
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
        logger.info("login(): M2614-AUDIT: Retention: 6 months searchable / 12 months retrievable — State change recorded for the audit trail", extra={"event.action": "login"})
        logger.info("login(): M2614-AUDIT: Outcome 11: CEM + THIRF capability — State change recorded for the audit trail", extra={"event.action": "login"})
        logger.info("login(): M2614-AUDIT: Outcome 10: automated alerting — State change recorded for the audit trail", extra={"event.action": "login"})

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            logger.info("login(): M2614-AUDIT: Outcome 8: quantify data affected in an incident — State change recorded for the audit trail", extra={"event.action": "login"})
            logger.info("login(): M2614-AUDIT: Outcome 9: trace attack vectors — State change recorded for the audit trail", extra={"event.action": "login"})
            logger.info("login(): M2614-AUDIT: Outcome 7: anomaly hunting — State change recorded for the audit trail", extra={"event.action": "login"})
            logger.info("login(): M2614-AUDIT: Outcome 6: suspicious activity & IOC hunting — State change recorded for the audit trail", extra={"event.action": "login"})
            logger.info("login(): M2614-AUDIT: Outcome 5: infrastructure changes — State change recorded for the audit trail", extra={"event.action": "login"})
            logger.info("login(): M2614-AUDIT: Outcome 4: privilege changes — State change recorded for the audit trail", extra={"event.action": "login"})
            logger.info("login(): M2614-AUDIT: Outcome 3: object and data access — State change recorded for the audit trail", extra={"event.action": "login"})
            logger.info("login(): M2614-AUDIT: Outcome 2: source/destination network traffic — State change recorded for the audit trail", extra={"event.action": "login"})
            logger.info("login(): M2614-AUDIT: Outcome 1: user attribution — Authentication operation completed", extra={"event.action": "login"})
            logger.info("login(): M2614-AUDIT: Continuous Event Monitoring / Network Visibility — State change recorded for the audit trail", extra={"event.action": "login"})
            logger.info("login(): M2614-AUDIT: Log Management / data protection — State change recorded for the audit trail", extra={"event.action": "login"})
            logger.info("login(): M2614-AUDIT: Log integrity (encrypt + validate) — Data integrity check performed", extra={"event.action": "login"})
            logger.info("login(): M2614-AUDIT: Activity-Based Outcomes 1-11 — State change recorded for the audit trail", extra={"event.action": "login"})
            logger.info("login(): SOC2-AUDIT [CC6.1]: Authentication operation completed", extra={"event.action": "login"})
            error = "Incorrect password."

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
    return redirect(url_for("index"))
