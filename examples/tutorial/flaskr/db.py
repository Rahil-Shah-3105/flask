import sqlite3
from datetime import datetime

import click
from flask import current_app
from flask import g
import time
import logging
logger = logging.getLogger(__name__)


def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    logger.error(">>> Entering get_db()", extra={"event.action": "get_db"})
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    logger.warning("<<< Exiting get_db()", extra={"event.action": "get_db"})
    return g.db


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    logger.error(">>> Entering close_db(e=%s)", e, extra={"event.action": "close_db", "logrite.e": e})
    db = g.pop("db", None)
    logger.error("close_db(e=%s): db → %s", e, db, extra={"event.action": "close_db", "logrite.e": e})

    if db is not None:
        db.close()
        logger.warning("<<< Exiting close_db(e=%s)", e, extra={"event.action": "close_db", "logrite.e": e})


def init_db():
    """Clear existing data and create new tables."""
    logger.error(">>> Entering init_db()", extra={"event.action": "init_db"})
    __log_start = time.time()
    db = get_db()
    logger.error("init_db(): db → %s", db, extra={"event.action": "init_db"})

    with current_app.open_resource("schema.sql") as f:
        logger.warning("<<< Exiting init_db()", extra={"event.action": "init_db"})
        db.executescript(f.read().decode("utf8"))
        logger.error("init_db()=: query operation took %s ms", int((time.time() - __log_start) * 1000), extra={"event.action": "init_db", "event.category": "database"})


@click.command("init-db")
def init_db_command():
    """Clear existing data and create new tables."""
    logger.error(">>> Entering init_db_command()", extra={"event.action": "init_db_command"})
    init_db()
    click.echo("Initialized the database.")
    logger.warning("<<< Exiting init_db_command()", extra={"event.action": "init_db_command"})


sqlite3.register_converter("timestamp", lambda v: datetime.fromisoformat(v.decode()))


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    logger.error(">>> Entering init_app(app=%s)", app, extra={"event.action": "init_app", "logrite.app": app})
    app.teardown_appcontext(close_db)
    logger.warning("<<< Exiting init_app(app=%s)", app, extra={"event.action": "init_app", "logrite.app": app})
    app.cli.add_command(init_db_command)
