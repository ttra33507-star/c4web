"""Flask route definitions."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from . import data
from .payway import PaywayClient, PaywayError

bp = Blueprint("main", __name__)


def _format_price(value: float) -> str:
    """Format a numeric price as a PayWay compliant string."""
    return str(
        Decimal(value).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
    )


@bp.get("/")
def home():
    return render_template("index.html", services=data.SERVICES)


@bp.get("/services")
def services_page():
    return render_template("services.html", services=data.SERVICES)


@bp.get("/contact")
def contact():
    return render_template("contact.html")


@bp.get("/dashboard")
def dashboard():
    return render_template(
        "dashboard/index.html",
        active="overview",
        licenses=data.LICENSE_DATA,
        orders=data.ORDER_HISTORY,
        history=data.TRANSACTION_HISTORY,
    )


@bp.get("/dashboard/license_keys")
def license_keys():
    return render_template(
        "dashboard/license_keys.html",
        active="licenses",
        licenses=data.LICENSE_DATA,
    )


@bp.get("/dashboard/order")
def order():
    return render_template(
        "dashboard/order.html",
        active="orders",
        orders=data.ORDER_HISTORY,
    )


@bp.get("/dashboard/transactions")
def transactions():
    return render_template(
        "dashboard/transactions.html",
        active="transactions",
        history=data.TRANSACTION_HISTORY,
    )


@bp.get("/service/<int:service_id>/order")
def order_service(service_id: int):
    if service_id < 0 or service_id >= len(data.SERVICES):
        abort(404)

    selected_service = data.SERVICES[service_id]
    return render_template("payment.html", service=selected_service, service_id=service_id)


@bp.post("/api/payments/aba/checkout")
def payway_checkout():
    """Create a hosted checkout payload for ABA PayWay."""
    request_data: dict[str, Any] | None = request.get_json(silent=True)
    if not request_data:
        abort(400, "Missing request body.")

    service_id = request_data.get("serviceId")
    customer = request_data.get("customer", {})

    if service_id is None or not isinstance(service_id, int):
        abort(400, "serviceId must be provided as an integer.")

    if service_id < 0 or service_id >= len(data.SERVICES):
        abort(404, "Selected service is not available.")

    service = data.SERVICES[service_id]
    amount = _format_price(service["price"])

    client = PaywayClient.from_app(current_app)

    try:
        checkout_payload = client.create_checkout_payload(
            order_id=f"ORDER-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            amount=amount,
            items=service["name"],
            customer=customer,
        )
    except PaywayError as exc:
        abort(502, str(exc))

    return jsonify(checkout_payload)


@bp.get("/payment/confirm")
def payment_confirm():
    return render_template("payment_success.html")


@bp.post("/payment/success")
def payment_success():
    """Handle the PayWay callback once a payment succeeds."""
    payload = request.form.to_dict()
    payload.setdefault("timestamp", datetime.utcnow().isoformat())
    payload.setdefault("status", "success")

    data.TRANSACTION_HISTORY["transactions"].append(payload)
    data.TRANSACTION_HISTORY["count"] = len(data.TRANSACTION_HISTORY["transactions"])

    try:
        amount = float(payload.get("amount", "0"))
    except ValueError:
        amount = 0.0
    data.TRANSACTION_HISTORY["total_amount"] += amount

    return redirect(url_for("main.dashboard"))
