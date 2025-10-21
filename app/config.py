"""Configuration objects for the Flask application."""

import os
from pathlib import Path


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

    _SQLITE_PATH = _default_sqlite_path()
    # Ensure the target directory exists before SQLAlchemy initialises.
    try:
        _SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        # Ignore failures so the application can surface a clearer DB error.
        pass

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        _sqlite_uri_from_path(_SQLITE_PATH),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    TELEGRAM_SUPPORT_URL = os.environ.get(
        "TELEGRAM_SUPPORT_URL",
        "https://t.me/C4SupportBot",
    )
