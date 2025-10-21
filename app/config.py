"""Configuration objects for the Flask application."""

import os
from pathlib import Path
from urllib.parse import quote_plus


_BASE_DIR = Path(__file__).resolve().parent.parent


def _default_sqlite_path() -> Path:
    """
    Determine where the SQLite file should live.

    On Vercel the function bundle is read-only, so persist to /tmp instead.
    Allow overriding with SQLITE_PATH when customising deployments.
    """
    if sqlite_path := os.environ.get("SQLITE_PATH"):
        return Path(sqlite_path)

    if os.environ.get("VERCEL"):
        return Path("/tmp") / "c4web.sqlite"

    return _BASE_DIR / "c4web.sqlite"


def _sqlite_uri_from_path(path: Path) -> str:
    """Convert an absolute filesystem path into a SQLAlchemy SQLite URI."""
    return f"sqlite:///{path.expanduser().resolve().as_posix()}"


def _resolve_database_uri() -> str:
    """
    Build the SQLAlchemy database URI from environment variables.

    Priority order:
        1. DATABASE_URL (full SQLAlchemy connection string)
        2. MYSQL_* variables (host, database, user, password, port)
        3. SQLite fallback stored alongside the project (or /tmp on Vercel)
    """
    if database_url := os.environ.get("DATABASE_URL"):
        return database_url

    mysql_host = os.environ.get("MYSQL_HOST")
    mysql_db = os.environ.get("MYSQL_DATABASE")
    mysql_user = os.environ.get("MYSQL_USER")

    if mysql_host and mysql_db and mysql_user:
        mysql_port = os.environ.get("MYSQL_PORT", "3306").strip() or "3306"
        mysql_password = os.environ.get("MYSQL_PASSWORD", "")
        mysql_charset = os.environ.get("MYSQL_CHARSET", "utf8mb4")

        user_part = quote_plus(mysql_user)
        password_part = f":{quote_plus(mysql_password)}" if mysql_password else ""

        # Allow passing host:port via MYSQL_HOST; otherwise append the port.
        host_part = mysql_host if ":" in mysql_host else f"{mysql_host}:{mysql_port}"
        db_part = quote_plus(mysql_db)
        charset_query = f"?charset={quote_plus(mysql_charset)}" if mysql_charset else ""

        return f"mysql+pymysql://{user_part}{password_part}@{host_part}/{db_part}{charset_query}"

    sqlite_path = _default_sqlite_path()
    try:
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        # Ignore failures so the application can surface a clearer DB error.
        pass
    return _sqlite_uri_from_path(sqlite_path)


class Config:
    """Base configuration loaded for every environment."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    ABA_PAYWAY_MERCHANT_ID = os.environ.get("ABA_PAYWAY_MERCHANT_ID", "YOUR_MERCHANT_ID")
    ABA_PAYWAY_API_KEY = os.environ.get("ABA_PAYWAY_API_KEY", "YOUR_API_KEY")
    ABA_PAYWAY_PUBLIC_KEY = os.environ.get("ABA_PAYWAY_PUBLIC_KEY", "YOUR_PUBLIC_KEY")

    ABA_PAYWAY_CHECKOUT_URL = os.environ.get(
        "ABA_PAYWAY_CHECKOUT_URL",
        "https://checkout.payway.com.kh/api/purchase",
    )
    ABA_PAYWAY_RETURN_URL = os.environ.get("ABA_PAYWAY_RETURN_URL", "http://localhost:5000/payment/confirm")
    ABA_PAYWAY_CANCEL_URL = os.environ.get("ABA_PAYWAY_CANCEL_URL", "http://localhost:5000/services")

    ABA_PAYWAY_TIMEOUT = int(os.environ.get("ABA_PAYWAY_TIMEOUT", "30"))

    SQLALCHEMY_DATABASE_URI = _resolve_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    TELEGRAM_SUPPORT_URL = os.environ.get(
        "TELEGRAM_SUPPORT_URL",
        "https://t.me/C4SupportBot",
    )
