# C4 Web

Backend Flask app with SQLite (default) or MySQL persistence and ABA PayWay integration.

## Requirements
- Python 3.11+
- Node.js 18+ (for Tailwind build only)
- (Optional) MySQL/MariaDB server (e.g. XAMPP) with a database named `c4web`

## Environment
The app now stores data in a local SQLite file (`c4web.sqlite`) by default.  
To switch to MySQL you can either provide a complete SQLAlchemy connection string via `DATABASE_URL` or set the individual `MYSQL_*` variables:

```
set DATABASE_URL=mysql+pymysql://<user>:<password>@localhost/c4web
# or
set MYSQL_HOST=localhost
set MYSQL_DATABASE=c4web
set MYSQL_USER=root
set MYSQL_PASSWORD=secret   # optional
set MYSQL_PORT=3306         # optional, defaults to 3306
set MYSQL_CHARSET=utf8mb4   # optional, defaults to utf8mb4

# optional: expose Telegram chat support
set TELEGRAM_SUPPORT_URL=https://t.me/<your_support_bot_or_username>
```

On Windows PowerShell replace `set` with `$env:DATABASE_URL = "..."`.

## First-Time Setup
1. Install Python dependencies: `pip install -r requirements.txt`
2. (MySQL only) Ensure the server is running and the `c4web` database exists (create via phpMyAdmin if needed). Configure either `DATABASE_URL` or the `MYSQL_*` variables before continuing.
3. Initialize tables and seed default services:
   - `python init_db.py`
4. Start the development server: `python run.py`

The service catalog, orders, and transaction logs now persist in MySQL. Use phpMyAdmin to inspect the `services`, `orders`, `users`, `payments`, `reports`, and `transactions` tables.

## Database Tables & API
- `orders`: storefront purchases created from the services catalog.
- `users`: customer profiles captured during checkout.  
  - API: `GET /api/users`, `POST /api/users`
- `payments`: ledger of captured/attempted gateway payments tied to orders.  
  - API: `GET /api/payments`, `POST /api/payments`
- `reports`: support/compliance reports.  
  - API: `GET /api/reports`, `POST /api/reports`, `PATCH /api/reports/<id>`
- `transactions`: raw ABA PayWay callbacks; successful callbacks mirror into `payments`.

Dashboard pages under `/dashboard/*` reflect each table (Overview, Users, Payments, Reports, Transactions).

## Tailwind (optional)
Install Node dependencies once: `npm install`

Rebuild CSS when styles change: `npm run build`

## Testing
Run syntax checks: `python -m compileall app`
