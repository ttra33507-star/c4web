"""Utility helpers for interacting with ABA PayWay."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Any

from flask import current_app


class PaywayError(RuntimeError):
    """Raised when an ABA PayWay interaction cannot be completed."""


@dataclass(slots=True)
class PaywayClient:
    merchant_id: str
    api_key: str
    public_key: str
    checkout_url: str
    return_url: str
    cancel_url: str
    timeout: int = 30

    @classmethod
    def from_app(cls, app) -> "PaywayClient":
        config = app.config

        client = cls(
            merchant_id=config.get("ABA_PAYWAY_MERCHANT_ID", ""),
            api_key=config.get("ABA_PAYWAY_API_KEY", ""),
            public_key=config.get("ABA_PAYWAY_PUBLIC_KEY", ""),
            checkout_url=config.get("ABA_PAYWAY_CHECKOUT_URL", ""),
            return_url=config.get("ABA_PAYWAY_RETURN_URL", ""),
            cancel_url=config.get("ABA_PAYWAY_CANCEL_URL", ""),
            timeout=config.get("ABA_PAYWAY_TIMEOUT", 30),
        )

        client._validate_configuration()
        return client

    @classmethod
    def from_current_app(cls) -> "PaywayClient":
        return cls.from_app(current_app._get_current_object())  # type: ignore[attr-defined]

    def _validate_configuration(self) -> None:
        if not self.merchant_id or self.merchant_id == "YOUR_MERCHANT_ID":
            raise PaywayError("ABA PayWay merchant ID has not been configured.")

        if not self.api_key or self.api_key == "YOUR_API_KEY":
            raise PaywayError("ABA PayWay API key has not been configured.")

        if not self.checkout_url:
            raise PaywayError("ABA PayWay checkout endpoint URL is missing.")

        if not self.return_url:
            raise PaywayError("ABA PayWay return URL is missing.")

        if not self.cancel_url:
            raise PaywayError("ABA PayWay cancel URL is missing.")

    def create_checkout_payload(
        self,
        order_id: str,
        amount: str,
        items: str,
        customer: dict[str, Any] | None = None,
        currency: str = "USD",
    ) -> dict[str, Any]:
        """Prepare the hosted checkout payload.

        Notes
        -----
        ABA PayWay validates the HMAC signature over a concatenated string of
        selected fields. The canonical order below reflects the public REST
        documentation (merchant_id, order_id, amount, items, currency, return_url,
        cancel_url). If your merchant account uses a different signing contract,
        adjust the ``signing_fields`` list to match.
        """
        payload: dict[str, Any] = {
            "merchant_id": self.merchant_id,
            "order_id": order_id,
            "amount": amount,
            "currency": currency,
            "items": items,
            "return_url": self.return_url,
            "cancel_url": self.cancel_url,
        }

        if customer:
            email = customer.get("email")
            phone = customer.get("phone")
            name = customer.get("name")

            if name:
                payload["customer_name"] = name
            if email:
                payload["customer_email"] = email
            if phone:
                payload["customer_phone"] = phone

        signing_fields = [
            "merchant_id",
            "order_id",
            "amount",
            "currency",
            "items",
            "return_url",
            "cancel_url",
        ]
        signing_string = "|".join(str(payload[field]) for field in signing_fields if payload.get(field))

        payload["hash"] = hmac.new(
            self.api_key.encode("utf-8"),
            signing_string.encode("utf-8"),
            hashlib.sha512,
        ).hexdigest()

        return {
            "endpoint": self.checkout_url,
            "payload": payload,
        }
