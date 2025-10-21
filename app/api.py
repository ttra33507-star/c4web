"""REST-style API blueprint providing JSON access to project data."""

from __future__ import annotations

from http import HTTPStatus
from datetime import datetime
from decimal import Decimal

from flask import Blueprint, abort, current_app, jsonify, request

from . import data
from .payway import PaywayClient, PaywayError

api = Blueprint("api", __name__, url_prefix="/api")


def _service_payload(service: dict) -> dict:
    return {
        "id": service["id"],
        "name": service["name"],
        "price": service["price"],
        "priceDisplay": f"${service['price']:.2f}",
        "image": service["image"],
        "description": service.get("desc"),
        "longDescription": service.get("long_description"),
    }


def _order_payload(order: dict) -> dict:
    return {
        "id": order["id"],
        "serviceId": order["service_id"],
        "serviceName": order["service"],
        "unitPrice": order.get("unit_price"),
        "quantity": order.get("quantity", 1),
        "total": order.get("amount"),
        "totalDisplay": order.get("price"),
        "status": order.get("status"),
        "customerName": order.get("customer"),
        "customer": order.get("customer_details") or {},
        "createdAt": order.get("created_at"),
        "updatedAt": order.get("updated_at"),
    }


def _transaction_payload(record: dict) -> dict:
    return {
        "tranId": record.get("tran_id"),
        "amount": record.get("amount_value"),
        "amountDisplay": record.get("amount"),
        "currency": record.get("currency"),
        "status": record.get("status"),
        "timestamp": record.get("timestamp"),
        "rawPayload": record.get("raw_payload", {}),
    }


def _user_payload(user: dict) -> dict:
    return {
        "id": user.get("id"),
        "fullName": user.get("fullName"),
        "email": user.get("email"),
        "phone": user.get("phone"),
        "company": user.get("company"),
        "createdAt": user.get("createdAt"),
        "updatedAt": user.get("updatedAt"),
    }


def _payment_payload(payment: dict) -> dict:
    return {
        "id": payment.get("id"),
        "orderId": payment.get("orderId"),
        "userId": payment.get("userId"),
        "amount": payment.get("amount"),
        "currency": payment.get("currency"),
        "method": payment.get("method"),
        "status": payment.get("status"),
        "gatewayReference": payment.get("gatewayReference"),
        "processedAt": payment.get("processedAt"),
    }


def _report_payload(report: dict) -> dict:
    return {
        "id": report.get("id"),
        "userId": report.get("userId"),
        "title": report.get("title"),
        "category": report.get("category"),
        "summary": report.get("summary"),
        "status": report.get("status"),
        "createdAt": report.get("createdAt"),
        "updatedAt": report.get("updatedAt"),
        "resolvedAt": report.get("resolvedAt"),
    }


@api.get("/health")
def healthcheck():
    """Simple liveliness probe."""
    return jsonify({"status": "ok"}), HTTPStatus.OK


@api.get("/services")
def list_services():
    """Expose the catalog of services."""
    services = [_service_payload(service) for service in data.list_services()]
    return jsonify({"services": services}), HTTPStatus.OK


@api.get("/services/<int:service_id>")
def retrieve_service(service_id: int):
    """Return a single service entry."""
    service = data.get_service(service_id)
    if service is None:
        abort(HTTPStatus.NOT_FOUND, description="Service not found.")
    return jsonify(_service_payload(service)), HTTPStatus.OK


@api.get("/orders")
def list_orders():
    """Return orders recorded in memory."""
    orders = [_order_payload(order) for order in data.list_orders()]
    return jsonify({"orders": orders}), HTTPStatus.OK


@api.post("/orders")
def create_order():
    """Create an order record associated with a service."""
    payload: dict | None = request.get_json(silent=True)
    if not payload:
        abort(HTTPStatus.BAD_REQUEST, description="Request body must be JSON.")

    service_id = payload.get("serviceId")
    quantity = payload.get("quantity", 1)
    customer = payload.get("customer") or {}

    if service_id is None or not isinstance(service_id, int):
        abort(HTTPStatus.BAD_REQUEST, description="`serviceId` must be provided as an integer.")

    service = data.get_service(service_id)
    if service is None:
        abort(HTTPStatus.NOT_FOUND, description="Selected service is not available.")

    user_record = None
    if isinstance(customer, dict):
        email = (customer.get("email") or "").strip()
        full_name = data.normalize_customer_name(customer)
        if email:
            user_record = data.create_user(
                full_name=full_name,
                email=email,
                phone=customer.get("phone"),
                company=customer.get("company"),
            )

    try:
        order = data.create_order_record(service_id, customer=customer, quantity=quantity)
    except IndexError:
        abort(HTTPStatus.NOT_FOUND, description="Selected service is not available.")

    if user_record:
        customer_details = order.get("customer_details") or {}
        customer_details["userId"] = user_record.get("id")
        order["customer_details"] = customer_details

    return jsonify(_order_payload(order)), HTTPStatus.CREATED


@api.get("/orders/<string:order_id>")
def retrieve_order(order_id: str):
    order = data.get_order(order_id)
    if order is None:
        abort(HTTPStatus.NOT_FOUND, description="Order not found.")
    return jsonify(_order_payload(order)), HTTPStatus.OK


@api.patch("/orders/<string:order_id>")
def mutate_order(order_id: str):
    payload: dict | None = request.get_json(silent=True)
    if not payload:
        abort(HTTPStatus.BAD_REQUEST, description="Request body must be JSON.")

    status = payload.get("status")
    if status is None:
        abort(HTTPStatus.BAD_REQUEST, description="`status` must be provided.")

    status_normalized = str(status).lower()
    allowed_statuses = {"pending", "processing", "paid", "cancelled", "refunded", "failed"}
    if status_normalized not in allowed_statuses:
        abort(
            HTTPStatus.BAD_REQUEST,
            description=f"`status` must be one of {', '.join(sorted(allowed_statuses))}.",
        )

    record = data.update_order_status(order_id, status_normalized)
    if record is None:
        abort(HTTPStatus.NOT_FOUND, description="Order not found.")

    return jsonify(_order_payload(record)), HTTPStatus.OK


@api.get("/transactions")
def list_transactions():
    history = data.transaction_summary()
    transactions = [_transaction_payload(txn) for txn in history["transactions"]]
    summary = {
        "count": history["count"],
        "totalAmount": round(history["total_amount"], 2),
    }
    return jsonify({"transactions": transactions, "summary": summary}), HTTPStatus.OK


@api.get("/users")
def list_users():
    users = [_user_payload(user) for user in data.list_users()]
    return jsonify({"users": users}), HTTPStatus.OK


@api.post("/users")
def create_user():
    payload: dict | None = request.get_json(silent=True)
    if not payload:
        abort(HTTPStatus.BAD_REQUEST, description="Request body must be JSON.")

    full_name = payload.get("fullName") or payload.get("name")
    email = payload.get("email")
    if not full_name or not email:
        abort(HTTPStatus.BAD_REQUEST, description="`fullName` and `email` are required.")

    record = data.create_user(
        full_name=full_name,
        email=email,
        phone=payload.get("phone"),
        company=payload.get("company"),
    )
    return jsonify(_user_payload(record)), HTTPStatus.CREATED


@api.get("/reports")
def list_reports():
    reports = [_report_payload(report) for report in data.list_reports()]
    return jsonify({"reports": reports}), HTTPStatus.OK


@api.post("/reports")
def create_report():
    payload: dict | None = request.get_json(silent=True)
    if not payload:
        abort(HTTPStatus.BAD_REQUEST, description="Request body must be JSON.")

    title = payload.get("title")
    if not title:
        abort(HTTPStatus.BAD_REQUEST, description="`title` is required.")

    report = data.create_report(
        title=title,
        summary=payload.get("summary"),
        category=payload.get("category"),
        status=payload.get("status", "open"),
        user_id=payload.get("userId"),
    )
    return jsonify(_report_payload(report)), HTTPStatus.CREATED


@api.patch("/reports/<int:report_id>")
def update_report(report_id: int):
    payload: dict | None = request.get_json(silent=True)
    if not payload:
        abort(HTTPStatus.BAD_REQUEST, description="Request body must be JSON.")

    status = payload.get("status", "resolved")
    report = data.resolve_report(report_id, status=status)
    if report is None:
        abort(HTTPStatus.NOT_FOUND, description="Report not found.")

    return jsonify(_report_payload(report)), HTTPStatus.OK


@api.get("/payments")
def list_payments():
    summary = data.payments_summary()
    payments = [_payment_payload(payment) for payment in summary["payments"]]
    payload = {
        "payments": payments,
        "summary": {
            "count": summary["count"],
            "totalAmount": round(summary["total_amount"], 2),
        },
    }
    return jsonify(payload), HTTPStatus.OK


@api.post("/payments")
def create_payment():
    payload: dict | None = request.get_json(silent=True)
    if not payload:
        abort(HTTPStatus.BAD_REQUEST, description="Request body must be JSON.")

    order_id = payload.get("orderId")
    amount = payload.get("amount")
    if not order_id or amount is None:
        abort(HTTPStatus.BAD_REQUEST, description="`orderId` and `amount` are required.")

    try:
        amount_value = Decimal(str(amount))
    except (ValueError, ArithmeticError):
        abort(HTTPStatus.BAD_REQUEST, description="`amount` must be numeric.")

    if data.get_order(order_id) is None:
        abort(HTTPStatus.NOT_FOUND, description="Order not found for payment.")

    record = data.record_payment(
        order_id=order_id,
        amount=amount_value,
        currency=payload.get("currency", "USD"),
        status=payload.get("status", "pending"),
        method=payload.get("method"),
        gateway_reference=payload.get("gatewayReference"),
        user_id=payload.get("userId"),
    )
    return jsonify(_payment_payload(record)), HTTPStatus.CREATED


@api.get("/licenses")
def list_licenses():
    licenses = list(data.list_licenses())
    return jsonify({"licenses": licenses}), HTTPStatus.OK


@api.post("/payments/aba/checkout")
def payway_checkout():
    """Create a hosted checkout payload for ABA PayWay."""
    request_data: dict | None = request.get_json(silent=True)
    if not request_data:
        abort(HTTPStatus.BAD_REQUEST, description="Missing request body.")

    service_id = request_data.get("serviceId")
    customer = request_data.get("customer", {})
    quantity = request_data.get("quantity", 1)
    order_id = request_data.get("orderId")

    if service_id is None or not isinstance(service_id, int):
        abort(HTTPStatus.BAD_REQUEST, description="`serviceId` must be provided as an integer.")

    service = data.get_service(service_id)
    if service is None:
        abort(HTTPStatus.NOT_FOUND, description="Selected service is not available.")

    order_record = None

    if order_id is not None:
        if not isinstance(order_id, str) or not order_id.strip():
            abort(HTTPStatus.BAD_REQUEST, description="`orderId` must be a non-empty string when provided.")
        order_record = data.get_order(order_id)
        if order_record is None:
            abort(HTTPStatus.NOT_FOUND, description="Referenced order could not be found.")
    else:
        order_record = data.create_order_record(service_id, customer=customer, quantity=quantity)
        order_id = order_record["id"]

    if isinstance(customer, dict) and customer:
        order_record["customer_details"] = customer
        order_record["customer"] = data.normalize_customer_name(customer)
        order_record["updated_at"] = datetime.utcnow().isoformat()

    amount_value = order_record.get("amount", service["price"])
    amount = f"{float(amount_value):.2f}"

    client = PaywayClient.from_app(current_app)

    try:
        checkout_payload = client.create_checkout_payload(
            order_id=order_id or f"ORDER-{order_id_component()}",
            amount=amount,
            items=service["name"],
            customer=customer,
        )
    except PaywayError as exc:
        abort(HTTPStatus.BAD_GATEWAY, description=str(exc))

    checkout_payload["orderId"] = order_id

    return jsonify(checkout_payload), HTTPStatus.OK


def order_id_component() -> str:
    from datetime import datetime

    return datetime.utcnow().strftime("%Y%m%d%H%M%S")
