"""Configuration objects for the Flask application."""

import os


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
