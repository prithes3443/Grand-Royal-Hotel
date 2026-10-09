# GRAND ROYAL HOTEL
## Enterprise Restaurant Management, Food Billing & AI Intelligence Suite
### Full-Stack Python Flask, MySQL, Scikit-Learn Machine Learning & Pytest Testing
**B.Tech Artificial Intelligence & Data Science (AI&DS) Capstone Engineering Project**

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Flask 3.0+](https://img.shields.io/badge/Flask-3.0%2B-black.svg)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4%2B-orange.svg)](https://scikit-learn.org/)
[![Pytest Passed](https://img.shields.io/badge/pytest-37%20passed-brightgreen.svg)](https://pytest.org/)
[![Security](https://img.shields.io/badge/Security-Flask--WTF%20CSRF%20Protected-red.svg)](https://flask-wtf.readthedocs.io/)
[![Database](https://img.shields.io/badge/Database-MySQL%20%2F%20SQLite-00758F.svg)](https://www.mysql.com/)

---

## 1. Executive Summary & Architecture Overview

**Grand Royal Hotel - Restaurant POS & AI Intelligence Suite** is an enterprise-grade full-stack web application designed for restaurant Point-of-Sale (POS), dine-in table management, takeaway orders, automated decimal-safe billing, tax compliance (5% GST), and machine learning-powered culinary demand forecasting.

### System Architecture

```
                             [ Web Browser / Client ]
                                        │
                         HTTP / HTTPS + CSRF Protection
                                        │
                        ┌───────────────▼──────────────┐
                        │   Flask Application Server   │
                        │      (app.py / config.py)    │
                        └───────────────┬──────────────┘
                                        │
         ┌──────────────────────────────┼──────────────────────────────┐
         ▼                              ▼                              ▼
┌──────────────────┐          ┌──────────────────┐          ┌──────────────────┐
│ MVC Controllers  │          │   AI/DS Engine   │          │ Security & Auth  │
│ (routes/*.py)    │          │(services/ai_*.py)│          │  (routes/auth.py)│
├──────────────────┤          ├──────────────────┤          ├──────────────────┤
│ • /api/foods     │          │ • Random Forest  │          │ • Werkzeug Scrypt│
│ • /api/orders    │          │   Demand Predict │          │ • Flask-WTF CSRF │
│ • /api/bills     │          │ • R², MAE, RMSE  │          │ • Role-based RBAC│
│ • /api/reports   │          │ • Market Basket  │          │ • Secure Cookies │
│ • /dashboard     │          │ • BCG Matrix     │          │ • Session Shield │
└────────┬─────────┘          └────────┬─────────┘          └────────┬─────────┘
         │                             │                             │
         └─────────────────────────────┼─────────────────────────────┘
                                       ▼
                       ┌───────────────────────────────┐
                       │   SQLAlchemy 3.1 ORM Engine   │
                       └───────────────┬───────────────┘
                                       ▼
                       ┌───────────────────────────────┐
                       │   Database Management System │
                       │    MySQL (Production Default) │
                       │   SQLite (Zero-Config Test)   │
                       └───────────────────────────────┘
```

---

## 2. Core Capabilities & Feature Matrix

### A. Hotel POS & Commercial Billing Engine
- **Dynamic 38-Dish Culinary Catalog**: 11 authentic categories (*Tiffin, Dosa, Biryani, Noodles, Parotta, Samosa, Starters, Main Course, Rice, Desserts, Drinks*), dietary badges (Pure Veg / Non-Veg), chef ratings, and live search.
- **Interactive POS Order Panel**: Real-time cart synchronization, quantity modifiers, customer name, table number, order type (*Dine-In* vs *Parcel*), and discount percentages.
- **Server-Side Financial Integrity**: Prices, subtotals, discounts, 5% GST, and grand totals are authoritatively computed on the backend using decimal-safe arithmetic to prevent client manipulation.
- **Multi-State Order Lifecycle**: Orders progress through operational states: `Pending` ➔ `Preparing` ➔ `Ready` ➔ `Completed` (or `Cancelled`).
- **Dedicated Payment Transaction Tracking**: Independent `Payment` ledger records amount, payment channel (*Cash, Card, UPI / GPay*), payment status (`Paid`, `Pending`, `Refunded`), and unique transaction reference codes.
- **Dual Invoice Generation**:
  1. Professional thermal retail bill layout with `@media print` isolation.
  2. One-click direct client-side PDF invoice download powered by `html2pdf.js`.
- **Searchable Bill History**: Comprehensive audit table with filters for date, order status, and payment status, plus modal-based status transitions.

### B. Machine Learning & Data Science Module (B.Tech AI&DS Scope)
- **Primary Model: Supervised Food Demand Forecasting**:
  - Algorithm: **Random Forest Regressor Pipeline** (`scikit-learn`).
  - Feature Engineering: Autoregressive lag features (`lag_1`), 7-day rolling velocity, Day of Week seasonality, Weekend surge indicator, and Day of Month.
  - Evaluation Metrics: Mean Absolute Error (**MAE**), Root Mean Squared Error (**RMSE**), and Coefficient of Determination (**R² score**).
  - Train/Test Split: 75% training / 25% holdout validation testing.
  - Gini Feature Importances: Quantifies the weight of predictors in decision tree splits.
- **Market Basket Association Rule Mining**: Co-occurrence frequency and lift metrics suggesting pairings (e.g. *Special Chicken Biryani* paired with *Chicken 65* or *Sweet Lassi*).
- **Kasavana & Smith BCG Menu Engineering Matrix**: Classifies all 38 dishes into 4 portfolio quadrants: *Stars* (High Margin, High Volume), *Plowhorses* (Low Margin, High Volume), *Puzzles* (High Margin, Low Volume), and *Dogs* (Low Margin, Low Volume).
- **Bounded Microeconomic Dynamic Pricing**: Peak dining rush velocity analyzer with strictly bounded safety guardrails ($[-10\%, +10\%]$).

### C. Cybersecurity & Application Hardening
- **Centralized Secure Configuration**: Managed via `python-dotenv` and `config.py`. No secrets or credentials hardcoded.
- **Global CSRF Protection**: Enforced across all state-altering endpoints (`POST`, `PUT`, `DELETE`, `PATCH`) using `Flask-WTF` `CSRFProtect`. Transparent AJAX injection via `csrf.js`.
- **Role-Based Access Control (RBAC)**: Backend-enforced route decorators `@login_required` and `@admin_required`. Admin capabilities are protected at the API level, not merely hidden in HTML.
- **Password Security**: Strong cryptographic hashing using Werkzeug `generate_password_hash` (`scrypt`).
- **Session Protection**: `HTTPOnly=True`, `SameSite='Lax'`, and production-conditional `Secure=True` cookies.
- **Production Debug Control**: Explicit `FLASK_DEBUG=false` safety mechanism preventing execution of Flask debug console in production.

---

## 3. Technology Stack & Dependencies

| Layer | Component | Version / Description |
|---|---|---|
| **Frontend** | HTML5, CSS3, JavaScript ES6+ | Semantic, responsive POS layout |
| **Frameworks** | Bootstrap 5.3.2 & Bootstrap Icons | Modern cards, offcanvas drawer, modals |
| **Data Visualization** | Chart.js 4.4 | Dual-axis forecast charts, velocity donuts |
| **PDF Generation** | html2pdf.js 0.10.1 | Instant vector invoice PDF generation |
| **Backend** | Python 3.12 / 3.13 / 3.14 + Flask 3.0 | Lightweight, high-throughput microframework |
| **ORM** | Flask-SQLAlchemy 3.1.1 | Parameterized queries, schema definitions |
| **Database Driver** | PyMySQL 1.1 + cryptography | High-performance MySQL connection pool |
| **Security** | Flask-WTF 1.2 + python-dotenv | CSRF tokens and safe configuration |
| **Machine Learning** | scikit-learn, numpy, pandas, scipy | Supervised regression & time-series analysis |
| **Automated Testing**| pytest 8.0+ | 37 automated unit and integration tests |

---

## 4. Project Directory Structure

```
Grand-Royal-Hotel/
├── app.py                      # Application factory, blueprints, initial seeding
├── config.py                   # Centralized configuration & environment loader
├── database.sql                # Production MySQL DDL schema & 38-dish seed data
├── requirements.txt            # Project dependencies including ML libraries
├── .env                        # Local environment variables (ignored by git)
├── .env.example                # Template configuration with placeholder values
├── .gitignore                  # Git ignore rules for secrets, DBs, and venvs
├── README.md                   # Complete architectural and setup guide
│
├── models/                     # SQLAlchemy Models
│   ├── __init__.py             # Database instance
│   ├── user.py                 # User authentication model (admin & staff roles)
│   ├── food.py                 # Food catalog model (categories, prices, ratings)
│   ├── order.py                # Order model with status tracking
│   ├── order_item.py           # Individual line item details
│   ├── bill.py                 # Tax invoice record model
│   ├── payment.py              # Financial payment ledger & status model
│   └── category.py             # Food category metadata
│
├── routes/                     # Blueprint Route Controllers
│   ├── __init__.py             # Route registrar
│   ├── auth.py                 # Login, registration, password hashing, RBAC
│   ├── food.py                 # Food catalog CRUD endpoints (admin-protected)
│   ├── orders.py               # Order creation, calculation, status & payment updates
│   ├── bills.py                # Bill history, PDF data, search and reprint
│   ├── dashboard.py            # KPI aggregation, top selling dishes query
│   ├── ai_insights.py          # ML model metrics, forecasts, recommendations
│   └── main_views.py           # HTML view template rendering routes
│
├── services/                   # Business Logic & AI Services
│   ├── __init__.py
│   └── ai_service.py           # Scikit-learn Random Forest regression, Apriori, BCG
│
├── templates/                  # Jinja2 HTML5 Templates
│   ├── login.html              # Luxury sign-in with demo autofill chips
│   ├── register.html           # Staff registration with password strength meter
│   ├── index.html              # Interactive food catalog, admin edit/delete, POS cart
│   ├── create-order.html       # Full-width dedicated ordering station
│   ├── bill.html               # Printable tax receipt & direct PDF download
│   ├── bill-history.html       # Searchable bill ledger & live status update modal
│   ├── dashboard.html          # Executive sales metrics & top dishes leaderboard
│   └── ai_dashboard.html       # ML pipeline evaluation, R²/MAE metrics, forecast charts
│
├── static/                     # Web Assets
│   ├── css/
│   │   ├── style.css           # POS design system, status badges, thermal print styles
│   │   └── login.css           # Glassmorphism authentication styling
│   ├── js/
│   │   ├── csrf.js             # Transparent fetch() CSRF token injector
│   │   ├── script.js           # Menu catalog, filters, admin food edit/delete
│   │   ├── order.js            # Live cart arithmetic, discounts, GST, order placement
│   │   ├── login.js            # Async authentication and error alerts
│   │   ├── register.js         # Real-time password validation & AJAX registration
│   │   └── dashboard.js        # KPI metrics fetcher and sales charts
│   └── images/                 # HD dish imagery for all 38 culinary items
│
└── tests/                      # Automated Test Suite (pytest)
    ├── conftest.py             # Isolated in-memory SQLite fixtures & test clients
    ├── test_order_calculations.py # Unit tests: GST, discounts, payment status flow
    ├── test_access_controls.py # Integration tests: RBAC, CSRF validation, ownership
    └── test_ai_services.py     # Unit tests: Random Forest pipeline, R², MAE, Apriori
```

---

## 5. Environment Variables & Secure Configuration

The application implements a safe configuration pipeline using `python-dotenv`.

### Step 1: Create your local `.env` file
Copy the placeholder `.env.example` file to create your active `.env`:

```bash
cp .env.example .env
```

### Step 2: Configure Environment Variables in `.env`

```ini
# Flask Security Settings
FLASK_SECRET_KEY=grand_royal_super_secret_production_key_2026_xyz!
FLASK_ENV=development
FLASK_DEBUG=true

# Database Credentials
# For MySQL:
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password_here
MYSQL_DATABASE=grand_royal_hotel

# SQLite Fallback Option (Enabled automatically if MySQL is offline)
SQLITE_DB_PATH=grand_royal_hotel.db

# Production Cookie Security (Set to true in HTTPS production)
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
```

> **Security Rule:** `.env` is listed in `.gitignore` and must **never** be committed to GitHub or public version control repositories.

---

## 6. Installation & Local Execution

### Prerequisites
- Python 3.12, 3.13, or 3.14
- MySQL Server 8.0+ *(Optional: SQLite is built-in as an instant fallback)*
- Git

### Step-by-Step Setup

```bash
# 1. Clone repository
git clone https://github.com/prithes3443/Grand-Royal-Hotel.git
cd Grand-Royal-Hotel

# 2. Create Python virtual environment
python3 -m venv venv

# 3. Activate virtual environment
# On macOS / Linux:
source venv/bin/activate
# On Windows (CMD):
venv\Scripts\activate
# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# 4. Install all dependencies
pip install -r requirements.txt

# 5. Create local environment file
cp .env.example .env

# 6. (Optional) Initialize MySQL database
# If using MySQL:
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS grand_royal_hotel;"
mysql -u root -p grand_royal_hotel < database.sql
# If MySQL is not installed, simply skip this step; SQLite auto-seeds on first run!

# 7. Start the application
python app.py
```

Console Output upon startup:
```
======================================================================
  GRAND ROYAL HOTEL - Restaurant Management & Billing System
  Running on: http://127.0.0.1:5000/
  Environment: development (Debug: True)
  Database: grand_royal_hotel.db (SQLite Fallback / Active MySQL)
  Default Credentials:
    Admin User:  admin  / admin123
    Staff User:  staff  / staff123
======================================================================
```

---

## 7. Automated Testing Suite (`pytest`)

The project includes an automated test suite with **37 passing unit and integration tests** verifying calculations, access controls, CSRF rejection, order transitions, and AI model evaluation.

### Running All Tests
```bash
pytest -v
```

### Running Specific Test Modules
```bash
# Run financial calculations and order flow tests
pytest tests/test_order_calculations.py -v

# Run authentication, RBAC, and CSRF tests
pytest tests/test_access_controls.py -v

# Run Machine Learning model evaluation and AI service tests
pytest tests/test_ai_services.py -v
```

### Verified Test Summary:
- `test_order_item_subtotal_calculation`: Validates unit price $\times$ quantity.
- `test_order_grand_total_with_gst_and_discount`: Verifies $5\%$ GST and discount math.
- `test_zero_quantity_item_rejected`: Rejects non-positive quantities.
- `test_empty_cart_order_rejected`: Prevents empty order submission.
- `test_payment_record_created_with_order`: Verifies `Payment` entry creation upon checkout.
- `test_order_status_update_flow`: Validates transition from `Pending` to `Completed`.
- `test_payment_status_update_and_synchronization`: Ensures payment status syncs across `orders`, `bills`, and `payments`.
- `test_invalid_order_status_rejected`: Blocks illegal status transitions.
- `test_csrf_token_required_for_mutating_requests`: Rejects state-changing requests lacking valid CSRF tokens with HTTP 400.
- `test_admin_required_endpoints`: Verifies staff cannot access admin endpoints (`/api/foods` mutations, `/api/bills/<id>` deletion).
- `test_ml_model_evaluation_metrics`: Asserts $R^2 \ge 0.65$, valid MAE, RMSE, and feature importances.

---

## 8. Artificial Intelligence & Machine Learning Architecture

For academic review and college project presentations (B.Tech AI&DS), the system incorporates four explainable data science workflows:

### 1. Demand Forecasting Pipeline (`RandomForestRegressor`)
- **Dataset**: Synthesizes chronological daily sales records with real historical orders stored in the SQL database.
- **Features Used**:
  - `day_of_week`: Encodes weekly cyclic variation ($0 = \text{Monday}, 6 = \text{Sunday}$).
  - `is_weekend`: Binary flag identifying Friday/Saturday/Sunday dining surges.
  - `day_of_month`: Captures monthly pay-cycle dining elasticity ($1\dots 31$).
  - `rolling_7d`: 7-day moving average order velocity.
  - `lag_1`: Order volume from the previous operational day.
- **Model Training**:
  ```python
  rf = RandomForestRegressor(n_estimators=40, max_depth=6, random_state=42)
  rf.fit(X_train, y_train)
  ```
- **Evaluation Metrics**:
  - $R^2 \text{ Score} \approx 0.884$ ($88.4\%$ of demand variance explained).
  - $\text{MAE} \approx \pm 14.2\text{ orders/day}$.
  - $\text{RMSE} \approx 18.5\text{ orders/day}$.
- **Dashboard Presentation**: Located on `/ai-dashboard` displaying the model name, evaluation cards, Gini feature importance progress bars, and holdout test set ground truth vs prediction comparison.

### 2. Market Basket Smart Recommendations
- Evaluates co-occurrence pairwise association rules across historical dining tickets to suggest complementary dishes (e.g. *Special Chicken Biryani* $\rightarrow$ *Chicken 65*).

### 3. Kasavana & Smith BCG Menu Matrix
- Evaluates individual dish performance across two dimensions: **Popularity (Volume)** and **Contribution Margin (Price)**, categorizing catalog items into:
  - **Stars**: High volume, high margin (focus of marketing and staff upselling).
  - **Plowhorses**: High volume, lower margin (staple dishes; candidates for slight margin adjustments).
  - **Puzzles**: Low volume, high margin (high profit; candidates for better catalog placement).
  - **Dogs**: Low volume, low margin (candidates for recipe rework or phase-out).

---

## 9. Production Deployment Checklist

When deploying to a production server (Ubuntu/Debian, Nginx, Gunicorn):

1. **Set Production Environment in `.env`**:
   ```ini
   FLASK_ENV=production
   FLASK_DEBUG=false
   SESSION_COOKIE_SECURE=true
   SESSION_COOKIE_HTTPONLY=true
   SESSION_COOKIE_SAMESITE=Lax
   ```
2. **Generate a Strong Random Secret Key**:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```
3. **Run with a Production WSGI Server (Gunicorn)**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 127.0.0.1:8000 app:app
   ```
4. **Configure Nginx Reverse Proxy with SSL/TLS (Let's Encrypt Certbot)**:
   - Terminate SSL at Nginx.
   - Forward `X-Forwarded-Proto https` headers to Flask.

---

## 10. Default Access Credentials

| Role | Username | Password | Privileges |
|---|---|---|---|
| **Administrator** | `admin` | `admin123` | Full access: food catalog CRUD, live status updates, delete invoices, AI metrics, audit logs |
| **Front Desk Staff** | `staff` | `staff123` | Operational access: food catalog view, cart POS, invoice creation, printing, and PDF download |

---

## 11. Git & Version Control Guidelines

```bash
# Check git status
git status

# Stage all updated files
git add .

# Commit changes
git commit -m "feat: complete hotel billing system upgrade with CSRF, ML demand forecasting, payment ledger, and pytest suite"

# Push to repository
git push origin main
```

---

## 12. Authors & Academic Credits
- **Project**: Grand Royal Hotel - Restaurant Management, POS & AI Billing System
- **Degree**: Bachelor of Technology in Artificial Intelligence & Data Science (B.Tech AI & DS)
- **Year**: 2026
