"""Utility script to bootstrap the database schema and seed data."""

from sqlalchemy.engine import make_url

from app import create_app, data
from app.extensions import db
from app.models import Order, Payment, Report, Service, Transaction, User


def _mask_database_uri(uri: str) -> str:
    """Render the database URI with any password redacted."""
    try:
        parsed = make_url(uri)
    except Exception:  # pragma: no cover - defensive fallback
        return uri

    if parsed.password:
        parsed = parsed.set(password="***")
    return str(parsed)


def main() -> None:
    app = create_app()

    with app.app_context():
        display_uri = _mask_database_uri(app.config["SQLALCHEMY_DATABASE_URI"])
        print(f"Using database: {display_uri}")

        db.create_all()
        data.ensure_seed_data()

        print("Database tables created and default services seeded.")
        print(
            "Counts => services: {services}, orders: {orders}, users: {users}, payments: {payments}, reports: {reports}, transactions: {transactions}".format(
                services=Service.query.count(),
                orders=Order.query.count(),
                users=User.query.count(),
                payments=Payment.query.count(),
                reports=Report.query.count(),
                transactions=Transaction.query.count(),
            )
        )


if __name__ == "__main__":
    main()
