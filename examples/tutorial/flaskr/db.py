import sqlite3
from datetime import datetime

import click
from flask import current_app
from flask import g
import logging
logger = logging.getLogger(app.name)


def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    logger.debug(">>> Entering get_db()")
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    logger.debug("<<< Exiting get_db()")
    return g.db


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    logger.debug(">>> Entering close_db(e=%s)", e)
    db = g.pop("db", None)
    logger.debug("close_db(e=%s): db → %s", e, db)

    if db is not None:
        db.close()
        logger.debug("<<< Exiting close_db(e=%s)", e)


def init_db():
    """Clear existing data and create new tables."""
    logger.debug(">>> Entering init_db()")
    import time; __log_start = time.time()
    db = get_db()
    logger.debug("init_db(): db → %s", db)
    logger.debug("<<< Exiting init_db()")

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))
        logger.error("Exception in init_db()", exc_info=True)
        logger.info("init_db()=: query operation took %s ms", int((time.time() - __log_start) * 1000))


@click.command("init-db")
def init_db_command():
    """Clear existing data and create new tables."""
    logger.debug(">>> Entering init_db_command()")
    init_db()
    click.echo("Initialized the database.")
    logger.debug("<<< Exiting init_db_command()")


sqlite3.register_converter("timestamp", lambda v: datetime.fromisoformat(v.decode()))


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    logger.debug(">>> Entering init_app(app=%s)", app)
    app.teardown_appcontext(close_db)
    logger.debug("<<< Exiting init_app(app=%s)", app)
    app.cli.add_command(init_db_command)
