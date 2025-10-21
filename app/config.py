"""Configuration objects for the Flask application."""

import os
from pathlib import Path


_BASE_DIR = Path(__file__).resolve().parent.parent
_DEFAULT_SQLITE_PATH = _BASE_DIR / "c4web.sqlite"


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

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{_DEFAULT_SQLITE_PATH.as_posix()}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    TELEGRAM_SUPPORT_URL = os.environ.get(
        "TELEGRAM_SUPPORT_URL",
        "https://t.me/C4SupportBot",
    )
