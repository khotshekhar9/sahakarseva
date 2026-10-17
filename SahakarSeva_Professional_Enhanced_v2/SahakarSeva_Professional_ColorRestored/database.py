"""
database.py - Database Initialization and Connection Management for SahakarSeva.
Provides the SQLAlchemy session instance, connection diagnostics, and schema helpers.
"""

import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

logger = logging.getLogger("sahakarseva.database")

# Canonical SQLAlchemy instance shared across models and application routes
db = SQLAlchemy()


def init_db(app):
    """Initialize the SQLAlchemy instance with Flask app and setup session handlers."""
    db.init_app(app)
    with app.app_context():
        try:
            # Quick non-blocking connection ping
            db.session.execute(text("SELECT 1"))
            logger.info("Database connection established successfully.")
        except Exception as exc:
            logger.warning("Database connection ping failed: %s", exc)


def ping_connection():
    """Verify active database connectivity. Returns (True, None) or (False, error_message)."""
    try:
        db.session.execute(text("SELECT 1"))
        return True, None
    except Exception as exc:
        return False, str(exc)


def get_table_counts():
    """Return dictionary of {table_name: row_count} across all mapped SQLAlchemy models."""
    counts = {}
    try:
        for table_name, table in db.metadata.tables.items():
            result = db.session.execute(text(f"SELECT COUNT(*) FROM `{table_name}`")).scalar()
            counts[table_name] = result or 0
    except Exception as exc:
        logger.error("Failed to query table counts: %s", exc)
    return counts


def is_database_seeded():
    """Check if the database has core demonstration records populated."""
    try:
        from models.communication import SystemSettings
        setting = SystemSettings.query.filter_by(key="demo_seeded").first()
        if setting and setting.value == "true":
            from models.user import User
            user_count = User.query.count()
            return user_count > 0
        return False
    except Exception:
        return False
