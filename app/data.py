"""Database-backed data helpers for the C4 application."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from itertools import count
from typing import Any, Iterable

from sqlalchemy.exc import SQLAlchemyError

from .extensions import db
from .models import Order, Payment, Report, Service, Transaction, User

LICENSE_DATA: list[dict[str, Any]] = []

DEFAULT_SERVICES: list[dict[str, Any]] = [
    {
        "name": "Auto Delete Comment - 1 Month Plan",
        "price": Decimal("9.99"),
        "image": "C4-Auto-Delete-Comment.png",
        "desc": "Kick-off automation with full feature access for 30 days.",
        "long_description": "Entry plan for teams validating their workflow. Includes all standard modules and support.",
    },
    {
        "name": "Facebook Station ",
        "price": Decimal("29.99"),
        "image": "C4-FB-Station.png",
        "desc": "Quarterly bundle with bonus days and premium feature unlocks.",
        "long_description": "Our most popular option—extend coverage, unlock additional rotations, and receive priority support.",
    },
    {
        "name": "Report Facebook ",
        "price": Decimal("119.99"),
        "image": "C4-Report-Facebook.png",
        "desc": "Annual coverage with native verification and custom feature access.",
        "long_description": "Full-year automation license with concierge onboarding, compliance review, and tailored feature drops.",
    },
    {
        "name": "Telegram Station",
        "price": Decimal("89.99"),
        "image": "C4-TG-Station.png",
        "desc": "Immersive audio with hybrid ANC for open offices.",
    },
    {
        "name": "Smart Desk Organizer",
        "price": Decimal("59.99"),
        "image": "txt.jpg",
        "desc": "Wireless charging, pen storage, and cable routing combined.",
    }
]

_CANONICAL_IMAGE_LOOKUP = {
    "c4_auto_delete_comment.png": "C4_Auto_Delete_Comment.png",
    "c4_fb_station.png": "C4_FB_Station.png",
    "c4_report_facebook.png": "C4_Report_Facebook.png",
    "c4_tg_station.png": "C4_TG_Station.png",
    "logo_c4_hub.png": "logo_C4_HUB.png",
    "logo_c4_tech_hub.png": "logo_C4_TECH_HUB.png",
    "txt.jpg": "txt.jpg",
}


def _normalize_static_image_name(name: str | None) -> str | None:
    """Ensure static asset names match the deployed file set."""
    if not name:
        return None

    sanitized = name.strip().replace(" ", "_")
    canonical = _CANONICAL_IMAGE_LOOKUP.get(sanitized.lower())
    return canonical or sanitized

PRICING_PLAN_DEFINITIONS: list[dict[str, Any]] = [
    {
        "service_name": "1 Month Automation Plan",
        "title": "1 Month",
        "price": Decimal("9.99"),
        "price_suffix": "/month",
        "features": [
            "2 time change key",
            "Bulk upload features",
            "Function schedule access",
            "Unlimited real device support",
            "Unlimited LDPlayer support",
        ],
        "variant": "standard",
    },
    {
        "service_name": "3 Month Automation Plan",
        "title": "3 Months",
        "price": Decimal("29.99"),
        "price_suffix": "/3 months",
        "badge": "Most popular",
        "features": [
            "+15 days free bonus",
            "10 time change key",
            "Bulk upload features",
            "Unlimited device & LDPlayer support",
            "Unlimited Facebook accounts",
        ],
        "variant": "highlight",
    },
    {
        "service_name": "12 Month Automation Plan",
        "title": "12 Months",
        "price": Decimal("119.99"),
        "price_suffix": "/year",
        "features": [
            "+30 days free bonus",
            "100 time change key",
            "Everything in 3 months plan",
            "Verify account natively",
            "Custom features on request",
        ],
        "variant": "standard",
    },
]

_ORDER_SEQUENCE = count(1)


def ensure_seed_data() -> None:
    """Populate the services table when empty."""
    existing_services = {service.name: service for service in Service.query.all()}
    updated = False

    for entry in DEFAULT_SERVICES:
        service = existing_services.get(entry["name"])
        normalized_image = _normalize_static_image_name(entry.get("image"))
        if service is None:
            service = Service(
                name=entry["name"],
                price=entry["price"],
                image=normalized_image,
                description=entry.get("desc"),
                long_description=entry.get("long_description"),
            )
            db.session.add(service)
            updated = True
        else:
            fields = {
                "price": entry["price"],
                "image": normalized_image,
                "description": entry.get("desc"),
                "long_description": entry.get("long_description"),
            }
            for attr, value in fields.items():
                if value is not None and getattr(service, attr) != value:
                    setattr(service, attr, value)
                    updated = True

    for service in Service.query.filter(Service.image.isnot(None)).all():
        normalized_image = _normalize_static_image_name(service.image)
        if normalized_image != service.image:
            service.image = normalized_image
            updated = True

    if updated:
        db.session.commit()


def _service_to_dict(service: Service) -> dict[str, Any]:
    return {
        "id": service.id,
        "name": service.name,
        "price": float(service.price),
        "image": _normalize_static_image_name(service.image),
        "desc": service.description,
        "long_description": service.long_description,
    }


def list_services() -> list[dict[str, Any]]:
    """Return all services stored in the database."""
    services = Service.query.order_by(Service.id.asc()).all()
    if not services:
        ensure_seed_data()
        services = Service.query.order_by(Service.id.asc()).all()

    if services:
        return [_service_to_dict(service) for service in services]

    # Fallback for environments where the database is unavailable.
    return [
        {
            "id": index + 1,
            "name": entry["name"],
            "price": float(entry["price"]),
            "image": _normalize_static_image_name(entry.get("image")),
            "desc": entry.get("desc"),
            "long_description": entry.get("long_description"),
        }
        for index, entry in enumerate(DEFAULT_SERVICES)
    ]


def list_pricing_plans() -> list[dict[str, Any]]:
    """Return pricing plan definitions with associated service metadata."""
    services = Service.query.order_by(Service.id.asc()).all()
    if not services:
        ensure_seed_data()
        services = Service.query.order_by(Service.id.asc()).all()

    services_by_name = {service.name: service for service in services}

    plans: list[dict[str, Any]] = []
    for definition in PRICING_PLAN_DEFINITIONS:
        service = services_by_name.get(definition["service_name"])
        price = service.price if service else definition.get("price", Decimal("0.00"))
        plan: dict[str, Any] = {
            "title": definition["title"],
            "price_value": float(price),
            "price_display": f"{Decimal(price):.2f}",
            "price_suffix": definition.get("price_suffix", ""),
            "features": definition.get("features", []),
            "badge": definition.get("badge"),
            "variant": definition.get("variant", "standard"),
            "service_id": service.id if service else None,
            "service_name": service.name if service else None,
        }
        plans.append(plan)
    return plans


def get_service(service_id: int) -> dict[str, Any] | None:
    """Fetch a service record by its primary key."""
    service = Service.query.get(service_id)
    if service is None:
        ensure_seed_data()
        service = Service.query.get(service_id)
    if service is None:
        return None
    return _service_to_dict(service)


def _coerce_quantity(raw_quantity: Any) -> int:
    try:
        quantity = int(raw_quantity)
    except (TypeError, ValueError):
        return 1
    return quantity if quantity > 0 else 1


def normalize_customer_name(customer: Any) -> str:
    if isinstance(customer, dict):
        return (
            customer.get("name")
            or customer.get("full_name")
            or customer.get("fullName")
            or "Guest"
        )
    if isinstance(customer, str):
        return customer
    return "Guest"


def _serialize_order(order: Order) -> dict[str, Any]:
    return {
        "id": order.id,
        "service_id": order.service_id,
        "service": order.service.name if order.service else None,
        "unit_price": float(order.unit_price),
        "quantity": order.quantity,
        "amount": float(order.amount),
        "price": order.price,
        "customer": order.customer_name,
        "customer_details": order.customer_details_dict(),
        "status": order.status,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "updated_at": order.updated_at.isoformat() if order.updated_at else None,
    }


def create_order_record(
    service_id: int,
    customer: dict[str, Any] | None = None,
    quantity: Any = 1,
) -> dict[str, Any]:
    """Persist an order in the database and return a serialized representation."""
    service = Service.query.get(service_id)
    if service is None:
        ensure_seed_data()
        service = Service.query.get(service_id)
    if service is None:
        raise IndexError("Service not found.")

    safe_quantity = _coerce_quantity(quantity)
    subtotal = Decimal(service.price) * Decimal(safe_quantity)
    now = datetime.utcnow()

    order_id = f"ORDER-{now.strftime('%Y%m%d%H%M%S')}-{next(_ORDER_SEQUENCE):04d}"
    customer_details = customer if isinstance(customer, dict) else {}

    order = Order(
        id=order_id,
        service_id=service.id,
        unit_price=service.price,
        quantity=safe_quantity,
        amount=subtotal,
        customer_name=normalize_customer_name(customer),
        customer_details=json.dumps(customer_details) if customer_details else None,
        status="pending",
        created_at=now,
        updated_at=now,
    )

    db.session.add(order)
    db.session.commit()

    return _serialize_order(order)


def list_orders() -> list[dict[str, Any]]:
    """Return database-backed orders ordered by recency."""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return [_serialize_order(order) for order in orders]


def get_order(order_id: str) -> dict[str, Any] | None:
    """Retrieve a stored order."""
    order = Order.query.get(order_id)
    if order is None:
        return None
    return _serialize_order(order)


def update_order_status(order_id: str, status: str) -> dict[str, Any] | None:
    """Mutate the status of an order, returning the updated record."""
    order = Order.query.get(order_id)
    if order is None:
        return None

    order.status = status
    order.updated_at = datetime.utcnow()
    db.session.commit()
    return _serialize_order(order)


def list_licenses() -> Iterable[dict[str, Any]]:
    """Expose the current license inventory."""
    return LICENSE_DATA


def list_users() -> list[dict[str, Any]]:
    """Return registered users sorted by recency."""
    users = User.query.order_by(User.created_at.desc()).all()
    return [user.to_dict() for user in users]


def create_user(
    full_name: str,
    email: str,
    phone: str | None = None,
    company: str | None = None,
) -> dict[str, Any]:
    """Persist a user record or return the existing one by email."""
    normalized_email = email.lower().strip()
    existing = User.query.filter_by(email=normalized_email).first()
    if existing:
        return existing.to_dict()

    user = User(
        full_name=full_name.strip(),
        email=normalized_email,
        phone=phone,
        company=company,
    )
    db.session.add(user)
    db.session.commit()
    return user.to_dict()


def list_payments() -> list[dict[str, Any]]:
    """Return payment attempts recorded in the system."""
    payments = Payment.query.order_by(Payment.processed_at.desc()).all()
    return [payment.to_dict() for payment in payments]


def record_payment(
    order_id: str,
    amount: Decimal | float,
    currency: str = "USD",
    status: str = "pending",
    method: str | None = None,
    gateway_reference: str | None = None,
    user_id: int | None = None,
) -> dict[str, Any]:
    """Create a payment record tied to an order."""
    if gateway_reference:
        existing = Payment.query.filter_by(gateway_reference=gateway_reference).first()
        if existing:
            existing.amount = Decimal(str(amount))
            existing.currency = currency
            existing.status = status
            existing.method = method
            if user_id:
                existing.user_id = user_id
            existing.processed_at = datetime.utcnow()
            db.session.commit()
            return existing.to_dict()

    payment = Payment(
        order_id=order_id,
        user_id=user_id,
        amount=Decimal(str(amount)),
        currency=currency,
        status=status,
        method=method,
        gateway_reference=gateway_reference,
    )
    db.session.add(payment)
    db.session.commit()
    return payment.to_dict()


def payments_summary() -> dict[str, Any]:
    """Return aggregate data for payments."""
    payments = Payment.query.all()
    total = sum(float(payment.amount) for payment in payments)
    return {
        "count": len(payments),
        "total_amount": round(total, 2),
        "payments": [payment.to_dict() for payment in payments],
    }


def list_reports() -> list[dict[str, Any]]:
    """Return submitted reports sorted by latest activity."""
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return [report.to_dict() for report in reports]


def create_report(
    title: str,
    summary: str | None = None,
    *,
    user_id: int | None = None,
    category: str | None = None,
    status: str = "open",
) -> dict[str, Any]:
    """Capture a support or audit report."""
    report = Report(
        title=title,
        summary=summary,
        user_id=user_id,
        category=category,
        status=status,
    )
    db.session.add(report)
    db.session.commit()
    return report.to_dict()


def resolve_report(report_id: int, status: str = "resolved") -> dict[str, Any] | None:
    """Mark a report as resolved."""
    report = Report.query.get(report_id)
    if report is None:
        return None

    report.status = status
    report.resolved_at = datetime.utcnow()
    report.updated_at = datetime.utcnow()
    db.session.commit()
    return report.to_dict()


def _serialize_transaction(transaction: Transaction) -> dict[str, Any]:
    payload = None
    if transaction.raw_payload:
        try:
            payload = json.loads(transaction.raw_payload)
        except json.JSONDecodeError:
            payload = {}

    return {
        "tran_id": transaction.tran_id,
        "amount": f"{Decimal(transaction.amount_value):.2f}",
        "amount_value": float(transaction.amount_value),
        "currency": transaction.currency,
        "status": transaction.status,
        "timestamp": transaction.timestamp.isoformat() if transaction.timestamp else None,
        "order_id": transaction.order_id,
        "raw_payload": payload or {},
    }


def list_transactions() -> list[dict[str, Any]]:
    """Return previously registered payment callbacks."""
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    return [_serialize_transaction(txn) for txn in transactions]


def register_transaction(payload: dict[str, Any]) -> dict[str, Any]:
    """Store a transaction payload and update aggregates."""
    status = (payload.get("status") or "success").lower()
    timestamp = payload.get("timestamp")
    if isinstance(timestamp, str):
        try:
            transaction_time = datetime.fromisoformat(timestamp)
        except ValueError:
            transaction_time = datetime.utcnow()
    else:
        transaction_time = datetime.utcnow()
    currency = payload.get("currency") or "USD"
    order_id = payload.get("order_id") or payload.get("orderId") or payload.get("orderID")

    try:
        amount_value = Decimal(str(payload.get("amount", 0)))
    except (TypeError, ValueError, ArithmeticError):
        amount_value = Decimal("0.00")

    tran_identifier = (
        payload.get("tran_id")
        or payload.get("transaction_id")
        or payload.get("transactionId")
        or payload.get("trans_id")
        or order_id
    )

    record = Transaction(
        order_id=order_id,
        tran_id=tran_identifier,
        amount_value=amount_value,
        currency=currency,
        status=status,
        timestamp=transaction_time,
        raw_payload=json.dumps(payload),
    )

    db.session.add(record)

    if order_id:
        order = Order.query.get(order_id)
        if order:
            canonical_status = "paid" if status == "success" else status
            order.status = canonical_status
            order.updated_at = datetime.utcnow()

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise

    if order_id and amount_value and status in {"success", "paid"}:
        payment_status = "captured" if status == "success" else status
        record_payment(
            order_id=order_id,
            amount=amount_value,
            currency=currency,
            status=payment_status,
            method="ABA PayWay",
            gateway_reference=tran_identifier,
        )

    return _serialize_transaction(record)


def transaction_summary() -> dict[str, Any]:
    """Return aggregate details alongside recent transactions."""
    transactions = list_transactions()
    total_amount = sum(entry["amount_value"] for entry in transactions)
    return {
        "count": len(transactions),
        "total_amount": round(total_amount, 2),
        "transactions": transactions,
    }
