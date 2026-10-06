# CarePoint — Hospital Management System (HMS)

CarePoint is a full-featured, educational Hospital Management System built with **Python 3**, **Flask**, **MySQL 8** (`mysql-connector-python`), **HTML5**, **CSS3** (Deep Teal theme), **JavaScript**, and **Bootstrap 5**. It serves as an academic DBMS minor project demonstrating core relational database concepts, including 3NF normalization, secure authentication (Sign In, Sign Up, Forgot Password with SMTP/token recovery, Reset Password, Change Password), ACID transactions, foreign key constraints, triggers, database views, complex JOINs, nested queries, safe read-only SQL playground, interactive ER diagram, and a 25+ question viva examination guide.

---

## 🌟 Key Features & Modules

### 1. Authentication & Security System
- **Sign In (`/login`)**: Login using either Username or Email, show/hide password toggle, Remember Me session permanence, anti-enumeration generic error messages.
- **Sign Up (`/signup`)**: Public registration with Full Name, Email, Username, Password, Confirm Password, password strength meter, duplicate account prevention, and non-admin role enforcement (`Receptionist`, `Doctor`).
- **Forgot Password (`/forgot-password`)**: Dedicated email-based password recovery flow. Generates cryptographically secure random tokens (`secrets` module), computes SHA-256 hashes, stores 30-minute expiration timestamps in MySQL, and delivers reset URLs via SMTP or safe local dev terminal logging. Uses generic non-enumerating responses ("If an account exists for that email, instructions to reset your password will be sent").
- **Reset Password (`/reset-password/<token>`)**: Token validation, expiration checks, single-use enforcement, new password confirmation, and atomic password update & token consumption inside a database transaction.
- **Change Password (`/change-password`)**: Authenticated user password update requiring verification of current password, new password confirmation, and session re-authentication.

### 2. Patient & Doctor Management
- **Patient Directory**: Full CRUD for patient demographic records, contact details, and emergency contacts.
- **Medical Staff**: Manage doctor profiles, specializations, consultation fees, and hospital department links.
- **Department Units**: Manage specialized medical departments (Cardiology, Neurology, Orthopedics, Pediatrics, Emergency).

### 3. Scheduling & Collision Prevention
- **Appointment Booking**: Schedule consultations linking patients, doctors, and departments.
- **Conflict Prevention**: Validates doctor schedule availability inside database transactions to prevent double-booking the same doctor at the same date/time slot.
- **Status Tracking**: Manage appointment states (`Scheduled`, `Completed`, `Cancelled`, `No-Show`).

### 4. Ward Admissions, Billing & Pharmacy
- **Inpatient Admissions**: Admit patients to available beds with row locking (`FOR UPDATE`) and automatic bed status updates (`Available` &rarr; `Occupied`).
- **Discharge Workflow**: Discharge inpatients and release assigned beds back to `Available` pool automatically.
- **Room & Bed Matrix**: Monitor General, Semi-Private, Private, and ICU bed availability and maintenance states.
- **Patient Invoices**: Create invoices, add itemized charges (room charges, doctor fees, medicines, procedures), record payments, and track balance due.
- **Pharmacy Inventory**: Track batch numbers, quantities, unit prices, expiry dates, and low-stock replenishment alerts (`quantity <= reorder_level`).
- **Atomic Dispensing**: Dispense prescriptions with stock reduction, inventory validation, and auto-billing inside transactions.

### 5. DBMS Demonstrators & SQL Lab
- **Safe SQL Playground**: Interactively test read-only SELECT queries (JOINs, subqueries, GROUP BY, views) with regex sanitization, multi-statement rejection, and a 100-row limit.
- **Interactive ER Diagram**: View 3NF entity-relationship diagram rendered via Mermaid.js, complete with cardinalities and schema dictionary.
- **Viva Examination Guide**: 25+ categorized question-and-answer pairs for project viva evaluation.

---

## 🛠 Tech Stack

- **Backend**: Python 3.13, Flask 3.1, Werkzeug
- **Database**: MySQL Server 8.0 (`mysql-connector-python`)
- **Security**: Cryptographic reset tokens (`secrets`), SHA-256 token hashing, Werkzeug scrypt password hashing, session RBAC
- **Email Delivery**: SMTP via `smtplib` / `EmailMessage` with local dev console logging fallback
- **Frontend**: HTML5, CSS3 (Teal `#0D4F59` & Turquoise `#00A896` theme), Vanilla JavaScript, Jinja2 Templates, Bootstrap 5 (CDN), FontAwesome 6 (CDN), Mermaid.js (CDN)
- **Testing**: Pytest 9.1

---

## 📁 Project Structure

```text
hospital_management_system/
├── app.py                      # Flask application entry point & blueprint registration
├── config.py                   # Environment & SMTP configuration loader
├── setup_db.py                 # Automated MySQL schema & seed runner
├── migrate_auth.py             # Idempotent database migration script for auth tables
├── requirements.txt            # Python package dependencies
├── .env.example                # Environment variables template
├── .env                        # Local database & SMTP credentials (ignored by Git)
├── .gitignore                  # Git ignore definitions
├── README.md                   # Project documentation
├── schema.sql                  # MySQL 8 relational database schema (3NF)
├── seed.sql                    # Fictional seed data for testing
│
├── database/
│   ├── __init__.py
│   ├── connection.py           # MySQL connection pool & cursor context manager
│   └── schema_notes.md         # Detailed 3NF schema architecture notes
│
├── services/
│   ├── __init__.py
│   ├── auth_service.py         # Token generation, SHA-256 hashing, SMTP reset email
│   ├── appointment_service.py  # Slot conflict detection & booking logic
│   ├── admission_service.py    # Transactional bed assignment & discharge
│   ├── billing_service.py      # Invoice generation, line items & payments
│   └── pharmacy_service.py     # Inventory tracking & atomic dispensing
│
├── routes/
│   ├── __init__.py
│   ├── auth.py                 # Login, signup, forgot/reset password & change password routes
│   ├── dashboard.py            # Dynamic metric counters calculated from MySQL
│   ├── patients.py             # Patient CRUD & search
│   ├── doctors.py              # Doctor directory & department filter
│   ├── departments.py          # Department management
│   ├── appointments.py         # Appointment booking & status update
│   ├── admissions.py           # Inpatient admission & discharge routes
│   ├── beds.py                 # Bed inventory & status matrix
│   ├── billing.py              # Billing ledger & payment recording
│   ├── pharmacy.py             # Inventory list & prescription dispensing
│   ├── reports.py              # Aggregated management reports
│   ├── sql_lab.py              # Safe read-only SQL playground
│   └── er_viva.py              # Interactive ER diagram & Viva QA viewer
│
├── static/
│   ├── css/style.css           # Custom deep teal & turquoise responsive styling
│   └── js/main.js              # Show/hide password, password strength meter, table filters
│
├── templates/
│   ├── base.html               # Base layout with sidebar navigation & header
│   ├── login.html              # Sign In page with show/hide password & Remember Me
│   ├── signup.html             # Sign Up page with role controls & strength feedback
│   ├── forgot_password.html    # Forgot Password email recovery form
│   ├── reset_password.html     # Reset Password token validation form
│   ├── change_password.html    # Authenticated user password update form
│   ├── dashboard.html          # Dynamic metrics grid & recent activity
│   ├── patients/               # Patient directory & registration form
│   ├── doctors/                # Doctor list & registration form
│   ├── departments/            # Department list & form
│   ├── appointments/           # Appointment list & booking form
│   ├── admissions/             # Admission list & ward bed allocation form
│   ├── beds/                   # Bed matrix list & modal
│   ├── billing/                # Invoice list, form, and detail view
│   ├── pharmacy/               # Inventory list, form, and dispense view
│   ├── reports/                # Aggregated analytical reports
│   ├── sql_lab/                # Safe SQL playground
│   ├── er_viva/                # ER diagram & Viva guide
│   └── errors/                 # Custom 404 & 500 error pages
│
└── tests/
    ├── __init__.py
    ├── test_auth.py            # Unit tests for hashing, tokens, expiration & roles
    ├── test_validation.py      # Unit tests for input validation
    └── test_services.py        # Unit tests for business logic math
```

---

## 🚀 Step-by-Step Setup Guide (Windows / VS Code)

### Prerequisites
1. **Python 3.10+**: Ensure Python is installed (`python --version`).
2. **MySQL Server 8.0**: Ensure MySQL Server is running locally on port `3306`.

---

### Step 1: Open Terminal & Activate Virtual Environment
Open PowerShell or VS Code Terminal in the project directory:

```powershell
# Create Python virtual environment
python -m venv venv

# Activate Virtual Environment (PowerShell)
.\venv\Scripts\Activate.ps1
```

> 💡 **PowerShell Troubleshooting**: If script execution is disabled on your system, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
> ```

---

### Step 2: Install Python Dependencies
Install the required packages:

```powershell
python -m pip install -r requirements.txt
```

---

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your local MySQL credentials and SMTP email configuration:

```env
SECRET_KEY=carepoint_super_secret_dev_key_2026

# Local MySQL Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_actual_mysql_root_password
DB_NAME=carepoint_hms

# Password Reset Settings
RESET_TOKEN_MAX_AGE_MINUTES=30

# SMTP Email Configuration (Optional - for real email sending)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_USE_TLS=True
SMTP_SENDER=noreply@carepoint.org

# Development Email Console Fallback (Safely prints reset link to local terminal console when SMTP is unconfigured)
DEV_EMAIL_CONSOLE=True
```

---

### Step 4: Database Migration / Initialization
For fresh setup:
```powershell
python setup_db.py
```

For existing CarePoint database instances (upgrading schema with `email` and `password_resets` table):
```powershell
python migrate_auth.py
```

---

### Step 5: Run the Flask Web Application
Launch the Flask development server:

```powershell
python app.py
```

Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 🔑 Fictional Demo Login Credentials

The database comes pre-seeded with 3 test user accounts:

| Role | Username | Email | Password | Access Level |
| :--- | :--- | :--- | :--- | :--- |
| **System Admin** | `admin` | `admin@carepoint.org` | `admin123` | Full system access to all modules & SQL Lab |
| **Receptionist** | `receptionist` | `receptionist@carepoint.org` | `reception123` | Patient registration, scheduling & admissions |
| **Doctor** | `dr_smith` | `dr_smith@carepoint.org` | `doctor123` | Medical directory & prescription dispensing |

---

## 🧪 Running Automated Unit Tests

Run the full unit test suite using `pytest`:

```powershell
python -m pytest tests/
```

**Expected Output:**
```text
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0
collected 8 items

tests\test_auth.py ....                                                  [ 50%]
tests\test_services.py ..                                                [ 75%]
tests\test_validation.py ..                                              [100%]

============================== 8 passed in 0.67s ==============================
```
