"""Utility script to bootstrap the database schema and seed data."""

from app import create_app
from app.extensions import db
from app import data
from app.models import Order, Payment, Report, Service, Transaction, User


def main() -> None:
    app = create_app()

    with app.app_context():
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
