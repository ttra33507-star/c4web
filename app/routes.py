"""Flask route definitions."""

from __future__ import annotations

from datetime import datetime
from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    request,
    url_for,
)

from . import data

bp = Blueprint("main", __name__)


@bp.get("/")
def home():
    services = data.list_services()
    pricing_plans = data.list_pricing_plans()
    plan_ids = {plan["service_id"] for plan in pricing_plans if plan["service_id"]}
    catalog_services = [service for service in services if service["id"] not in plan_ids]

    return render_template(
        "index.html",
        services=services,
        pricing_plans=pricing_plans,
        catalog_services=catalog_services,
    )


@bp.get("/services")
def services_page():
    return render_template("services.html", services=data.list_services())


@bp.get("/contact")
def contact():
    return render_template("contact.html")


@bp.get("/dashboard")
def dashboard():
    payments = data.payments_summary()
    return render_template(
        "dashboard/index.html",
        active="overview",
        licenses=data.list_licenses(),
        orders=data.list_orders(),
        history=data.transaction_summary(),
        users=data.list_users(),
        payments=payments,
        reports=data.list_reports(),
    )


@bp.get("/dashboard/license_keys")
def license_keys():
    return render_template(
        "dashboard/license_keys.html",
        active="licenses",
        licenses=list(data.list_licenses()),
    )


@bp.get("/dashboard/order")
def order():
    return render_template(
        "dashboard/order.html",
        active="orders",
        orders=data.list_orders(),
    )


@bp.get("/dashboard/transactions")
def transactions():
    return render_template(
        "dashboard/transactions.html",
        active="transactions",
        history=data.transaction_summary(),
    )


@bp.get("/dashboard/users")
def users():
    return render_template(
        "dashboard/users.html",
        active="users",
        users=data.list_users(),
    )


@bp.get("/dashboard/payments")
def payments():
    summary = data.payments_summary()
    return render_template(
        "dashboard/payments.html",
        active="payments",
        payments=summary["payments"],
        summary=summary,
    )


@bp.get("/dashboard/reports")
def reports():
    return render_template(
        "dashboard/reports.html",
        active="reports",
        reports=data.list_reports(),
    )


@bp.get("/service/<int:service_id>/order")
def order_service(service_id: int):
    service = data.get_service(service_id)
    if service is None:
        abort(404)

    return render_template(
        "payments.html",
        service=service,
        service_id=service["id"],
        pricing_plans=data.list_pricing_plans(),
    )

@bp.get("/payment/confirm")
def payment_confirm():
    return render_template("payment_success.html")


@bp.post("/payment/success")
def payment_success():
    """Handle the PayWay callback once a payment succeeds."""
    payload = request.form.to_dict()
    payload.setdefault("timestamp", datetime.utcnow().isoformat())
    payload.setdefault("status", "success")

    data.register_transaction(payload)

    return redirect(url_for("main.dashboard"))
