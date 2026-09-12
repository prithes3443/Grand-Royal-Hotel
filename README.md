# GRAND ROYAL HOTEL
## Restaurant & Food Ordering and Billing Management System
### Full-Stack Python Flask & MySQL Web Application

---

## 1. Project Introduction
**Grand Royal Hotel - Restaurant & Food Ordering and Billing Management System** is a production-ready, full-stack college capstone web application designed for restaurant Point-of-Sale (POS), dine-in table ordering, parcel takeaway billing, receipt generation, and real-time revenue analytics.

Built using an MVC (Model-View-Controller) architecture, the system provides separate operational privileges for **Administrators** (managing menus, viewing analytical performance, deleting bills) and **Front Desk Staff** (creating orders, calculating taxes/discounts, generating and printing invoices).

---

## 2. Key Features

- **Role-Based Authentication**:
  - Secure password hashing using Werkzeug (`scrypt`).
  - Roles: `ADMIN` and `STAFF`.
  - Session protection and automatic redirection on unauthenticated requests.
- **Dynamic Restaurant Menu Catalog**:
  - 38+ authentic culinary dishes across 11 categories (*Tiffin, Dosa, Biryani, Noodles, Parotta, Samosa, Starters, Main Course, Rice, Desserts, Drinks*).
  - High-definition culinary imagery, pure veg / non-veg dietary indicators, and chef ratings.
  - Real-time instant live search and category filtering.
- **Interactive POS Order Panel**:
  - Add dishes, increase/decrease quantities, or remove items.
  - Customer name and Table/Token number assignment.
  - Order type selector (*Dine-In* vs *Parcel / Takeaway*).
  - Live client-side calculation of subtotal, customizable discount %, and 5% GST.
  - Multi-channel payment options (*Cash, Card, UPI / GPay*).
- **Server-Side Integrity & Billing Engine**:
  - Authoritative re-calculation of all line items, subtotals, taxes, and totals in Flask backend before database storage to eliminate client manipulation.
  - Auto-generation of unique non-duplicating numbers (`ORD-1001`, `BILL-1001`).
- **Professional Printable Invoice**:
  - Printable retail receipt matching restaurant standards with hotel GSTIN, FSSAI numbers, breakdown of dishes, GST, discount, and grand total.
  - Thermal receipt printing stylesheet with `@media print` isolation.
- **Audit & Bill History**:
  - Chronological log of all recorded bills.
  - Live search by Bill #, Customer Name, or Table.
  - Date filtering (`YYYY-MM-DD`).
  - Actions: Reprint invoice, view line items modal, and admin delete privileges.
- **Executive Analytics Dashboard**:
  - 4 Real-time KPI Stat Cards: *Today's Orders, Today's Revenue, Total Orders Recorded, Total Food Revenue*.
  - Live recent invoices table with instant reprint shortcuts.
  - Leaderboard of Top Selling Dishes ranked by total quantity ordered using SQL aggregation (`GROUP BY` and `SUM`).
- **Admin Food Management**:
  - Add new dishes, set prices, update descriptions, select images, and toggle availability (*Available / Sold Out*).

---

## 3. Technology Stack

- **Frontend**:
  - HTML5 & CSS3
  - JavaScript (ES6+ Classes & Async Fetch API)
  - Bootstrap 5.3.2 (Responsive Grid, Modals, Forms, Toasts)
  - Bootstrap Icons
  - Google Fonts (Inter & Courier Prime)
- **Backend**:
  - Python 3.12+ (Compatible with Python 3.12, 3.13, 3.14)
  - Flask 3.0+
  - Flask-SQLAlchemy 3.1+
  - Werkzeug (Secure Password Hashing)
  - PyMySQL & Cryptography
- **Database**:
  - MySQL (with built-in automatic SQLite fallback for zero-configuration local testing)

---

## 4. Project Folder Structure

```
Grand-Royal-Hotel/
│
├── app.py                     # Flask Application factory & database auto-seed
├── config.py                  # Database & environment configurations
├── requirements.txt           # Python package dependencies
├── database.sql               # MySQL DDL schema and 38 dishes seed script
├── README.md                  # Complete documentation and setup guide
│
├── models/                    # SQLAlchemy MVC Data Models
│   ├── __init__.py            # DB instance
│   ├── user.py                # User auth model (admin & staff roles)
│   ├── food.py                # Food item model with categories & prices
│   ├── order.py               # Order master model
│   ├── order_item.py          # Line item details model
│   └── bill.py                # Final invoice model
│
├── routes/                    # Flask MVC Controllers / Blueprints
│   ├── __init__.py            # Blueprint registry
│   ├── auth.py                # Login, logout, session management
│   ├── food.py                # Food API (GET, POST, PUT, DELETE)
│   ├── orders.py              # Server-side validated order calculation & creation
│   ├── bills.py               # Bill history, search, and invoice rendering
│   ├── dashboard.py           # Real-time KPI analytics & top dishes query
│   └── main_views.py          # HTML page routes
│
├── templates/                 # Jinja2 HTML5 Views
│   ├── login.html             # Luxury login page with demo autofill
│   ├── index.html             # Menu catalog & POS live order panel
│   ├── dashboard.html         # Revenue analytics & culinary leaderboard
│   ├── bill-history.html      # Searchable invoice audit table
│   ├── create-order.html      # Full-width dedicated ordering screen
│   └── bill.html              # Printable thermal/retail tax receipt
│
└── static/                    # Static Assets
    ├── css/
    │   ├── style.css          # Main POS design system & print styles
    │   └── login.css          # Login page glassmorphic styles
    │
    ├── js/
    │   ├── script.js          # Menu catalog, search, category filter, admin modal
    │   ├── login.js           # Password toggling and async auth
    │   ├── order.js           # Live cart calculations, discount, GST, and submission
    │   └── dashboard.js       # Dashboard KPI metric fetcher & leaderboard renderer
    │
    └── images/                # HD Food & Beverage Images
        ├── idly.jpg
        ├── dosa.jpg
        ├── biryani.jpg
        ├── noodles.jpg
        ├── parotta.jpg
        ├── samosa.jpg
        ├── medu_vada.jpg
        ├── chicken65.jpg
        ├── tandoori.jpg
        ├── friedrice.jpg
        ├── paneer.jpg
        ├── coffee.jpg
        └── desserts.jpg
```

---

## 5. MySQL Installation

### Windows:
1. Download and install **MySQL Community Server** from [https://dev.mysql.com/downloads/installer/](https://dev.mysql.com/downloads/installer/).
2. During setup, choose default port `3306` and set a root password (e.g., `password` or `root`).

### macOS (via Homebrew):
```bash
brew install mysql
brew services start mysql
```

### Linux (Ubuntu / Debian):
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
```

---

## 6. Database Creation & Importing `database.sql`

Open your MySQL terminal, MySQL Workbench, or phpMyAdmin, and run:

```bash
mysql -u root -p < database.sql
```

Or execute in MySQL interactive shell:
```sql
CREATE DATABASE grand_royal_hotel;
USE grand_royal_hotel;
SOURCE /path/to/database.sql;
```

> **Zero-Configuration Fallback:** If MySQL is not running on your local machine during evaluation, the application automatically initializes a high-performance local SQLite database (`grand_royal_hotel.db`) with identical schema, admin/staff users, and all 38 dishes.

---

## 7. Python Installation
Ensure Python 3.12 or higher is installed:
```bash
python3 --version
```
Download from [https://www.python.org/downloads/](https://www.python.org/downloads/) if needed.

---

## 8. Virtual Environment Setup

### macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows (Command Prompt):
```cmd
python -m venv venv
venv\Scripts\activate
```

### Windows (PowerShell):
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

---

## 9. Installing Requirements
With your virtual environment activated, install all required dependencies:
```bash
pip install -r requirements.txt
```

---

## 10. Configuration (`config.py`)
Database connection credentials can be customized in `config.py` or via environment variables:
```python
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'password')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'grand_royal_hotel')
```

---

## 11. Running the Flask Web Application
Run the main application script:
```bash
python app.py
```

Console Output:
```
=======================================================
 GRAND ROYAL HOTEL - Restaurant & Food Billing System 
 Running on http://127.0.0.1:5000/
 Admin Login: admin / admin123
 Staff Login: staff / staff123
=======================================================
```

---

## 12. Opening the Application in Your Browser
Open your browser and visit:
```
http://127.0.0.1:5000/
```

---

## 13. Demo Login Credentials

| Role | Username | Password | Access Privileges |
|---|---|---|---|
| **ADMIN** | `admin` | `admin123` | Full Access: Manage food menu, add dishes, delete bills, view analytics |
| **STAFF** | `staff` | `staff123` | Billing Access: Create orders, generate receipts, view history, print bills |

> *Tip: On the login page, you can click on the demo credential chips to autofill instantly.*

---

## 14. Admin Demonstration Workflow

1. Navigate to `http://127.0.0.1:5000/login`.
2. Log in with `admin` / `admin123`.
3. Notice the **Admin Badge** on the top navigation bar.
4. Click **Add Dish** in the top navbar:
   - Fill in name (e.g. *Butter Naan*), price (e.g. *₹45*), category (*Main Course*), and food image.
   - Click **Save Dish to Menu**. The dish immediately becomes available in the catalog!
5. Open **Dashboard**:
   - Inspect the 4 KPI cards calculating live metrics from the database.
   - Review the **Top Selling Dishes** leaderboard.
6. Open **Bill History**:
   - Note the active **Delete (Trash)** button available exclusively to Admin users.

---

## 15. Staff Demonstration Workflow

1. Log in with `staff` / `staff123`.
2. Browse the **Food Menu**:
   - Filter by categories (*Tiffin, Biryani, Starters, Dosa, etc.*).
   - Filter by *Pure Veg* or *Non-Veg*.
   - Use the dynamic search bar (e.g., search *"Biryani"*).
3. Build an Order:
   - Click **ADD +** on *Special Chicken Biryani* and *Crispy Ghee Roast Dosa*.
   - Adjust quantities using `+` and `-`.
   - Enter Customer Name (*Ramesh Kumar*) and Table Number (*Table 4*).
   - Enter a Discount percentage (e.g., `10%`).
   - Notice the instant live updates to Subtotal, Discount, 5% GST, and Grand Total.
4. Generate Bill:
   - Select Payment Method (*UPI / GPay*).
   - Click **GENERATE & PRINT BILL**.
5. View & Print Invoice:
   - The system validates server-side and displays the official Tax Invoice.
   - Click **PRINT BILL** to test the thermal receipt print preview (`@media print`).
6. Navigate to **Bill History** to see the new invoice recorded in MySQL with live search and date filters.

---

## 16. College Project Evaluation Highlights

1. **True Full-Stack**: Python Flask backend + SQLAlchemy ORM + MySQL/SQLite + Modern JavaScript frontend.
2. **Security & Integrity**: Password hashing via Werkzeug (`scrypt`), role-based protection, server-side bill verification.
3. **Professional UX**: Red & dark slate palette matching modern hospitality apps (Zomato/Swiggy POS), micro-animations, and thermal receipt print isolation.
4. **Complete Documentation**: Full database scripts, requirements, and clean MVC separation.
