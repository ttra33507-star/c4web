"""Database models for the C4 web application."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func

from .extensions import db


class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    long_description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    orders = db.relationship("Order", back_populates="service", lazy="select")

    @property
    def desc(self) -> str | None:  # pragma: no cover - simple alias for templates
        return self.description

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "price": float(self.price),
            "image": self.image,
            "desc": self.description,
            "long_description": self.long_description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.String(64), primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    customer_name = db.Column(db.String(255), nullable=True)
    customer_details = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(32), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    service = db.relationship("Service", back_populates="orders", lazy="joined")
    transactions = db.relationship(
        "Transaction",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="select",
    )
    payments = db.relationship(
        "Payment",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="select",
    )

    @property
    def price(self) -> str:
        return f"${Decimal(self.amount):.2f}"

    @property
    def customer(self) -> str | None:
        return self.customer_name

    def customer_details_dict(self) -> dict:
        if not self.customer_details:
            return {}
        try:
            return json.loads(self.customer_details)
        except json.JSONDecodeError:  # pragma: no cover - defensive
            return {}

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "service_id": self.service_id,
            "service": self.service.name if self.service else None,
            "unit_price": float(self.unit_price),
            "quantity": self.quantity,
            "amount": float(self.amount),
            "price": self.price,
            "customer": self.customer_name,
            "customer_details": self.customer_details_dict(),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.String(64), db.ForeignKey("orders.id"), nullable=True)
    tran_id = db.Column(db.String(64), nullable=True, unique=True)
    amount_value = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    currency = db.Column(db.String(8), nullable=False, default="USD")
    status = db.Column(db.String(32), nullable=False, default="success")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    raw_payload = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    order = db.relationship("Order", back_populates="transactions", lazy="joined")

    def to_dict(self) -> dict:
        return {
            "tran_id": self.tran_id,
            "amount": f"{Decimal(self.amount_value):.2f}",
            "amount_value": float(self.amount_value),
            "currency": self.currency,
            "status": self.status,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "order_id": self.order_id,
            "raw_payload": self.raw_payload and json.loads(self.raw_payload),
        }

    @staticmethod
    def summary() -> dict:
        total_amount = (
            db.session.query(func.coalesce(func.sum(Transaction.amount_value), 0)).scalar()
            or 0
        )
        count = db.session.query(func.count(Transaction.id)).scalar() or 0
        return {
            "count": int(count),
            "total_amount": float(total_amount),
        }


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(32), nullable=True)
    company = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    reports = db.relationship("Report", back_populates="user", lazy="select")
    payments = db.relationship("Payment", back_populates="user", lazy="select")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "fullName": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "company": self.company,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.String(64), db.ForeignKey("orders.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(8), nullable=False, default="USD")
    method = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(32), nullable=False, default="pending")
    gateway_reference = db.Column(db.String(128), nullable=True, unique=True)
    processed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    order = db.relationship("Order", back_populates="payments", lazy="joined")
    user = db.relationship("User", back_populates="payments", lazy="joined")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "orderId": self.order_id,
            "userId": self.user_id,
            "amount": float(self.amount),
            "currency": self.currency,
            "method": self.method,
            "status": self.status,
            "gatewayReference": self.gateway_reference,
            "processedAt": self.processed_at.isoformat() if self.processed_at else None,
        }


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(64), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(32), nullable=False, default="open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    resolved_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="reports", lazy="joined")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "userId": self.user_id,
            "title": self.title,
            "category": self.category,
            "summary": self.summary,
            "status": self.status,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "resolvedAt": self.resolved_at.isoformat() if self.resolved_at else None,
        }
