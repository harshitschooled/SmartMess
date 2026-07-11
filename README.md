# SMARTMESS – Mess Management and Food Waste Reduction System

SmartMess is a beginner-friendly Python web application built using the Flask web framework. It addresses food waste in college mess halls and dining centers by allowing students to declare whether they will eat or skip upcoming meals before specific booking deadlines. Mess administrators can use these projections to prepare the exact amount of food needed, log food waste statistics in kilograms, review student feedback, and analyze metrics to optimize operations.

---

## 1. Project Problem & Solution
### Problem Statement
College mess kitchens prepare food for thousands of students daily without knowing exactly how many will show up for any given meal (Breakfast, Lunch, or Dinner). This leads to:
1. **Severe Food Wastage**: Unused food is discarded at the end of the day.
2. **Inconsistent Quality/Portions**: Kitchens under-prepare or over-prepare based on rough estimates.
3. **High Resource Overhead**: Financial losses for administrators due to excess raw material purchases.

### Solution
SmartMess introduces an **attendance-based booking mechanism**. Students indicate whether they are **Eating** or **Skipping** each meal before pre-configured closing deadlines. The system then aggregates these bookings into precise attendance projections, allowing kitchen staff to cook exactly what is needed.

---

## 2. Core Features
- **Student Dashboard**: View today's menu, check booking statuses, submit feedback, and view past booking history.
- **Meal Booking**: Create-or-update logic to declare eating/skipping choice before closing deadlines.
- **Booking Deadlines**:
  - *Breakfast* closes at 9:00 PM on the previous day.
  - *Lunch* closes at 9:00 AM on the same day.
  - *Dinner* closes at 3:00 PM on the same day.
- **Admin Dashboard**: View total students registered, expected attendances for today's meals, and recent log lists.
- **Menu Management**: Full CRUD capabilities for menus (create, read, update, delete by date).
- **Food Waste Tracking**: Log food prepared and consumed in kilograms (kg) and auto-derive food wasted and waste percentages.
- **Feedback System**: Collect student ratings (1 to 5) and textual suggestions per meal.
- **Interactive Analytics**: Graphical trends of attendance, meal-wise aggregates, and food waste using Chart.js.
- **CSV Data Export**: Export bookings, food waste, and feedback logs using Python's native `csv` module.

---

## 3. Technology Stack
- **Backend Framework**: Python 3, Flask
- **Database**: SQLite, Flask-SQLAlchemy (ORM)
- **Session & Auth**: Flask-Login, Werkzeug password hashing
- **Frontend Styling**: HTML5, Vanilla CSS3, Bootstrap 5 (CSS framework)
- **Charts/Graphs**: Chart.js
- **Form Verification**: Flask-WTF (with CSRF Protection)
- **Unit Testing**: Pytest

---

## 4. Folder Structure
```
smartmess/
├── app/
│   ├── __init__.py           # Application Factory, Extension bindings, Error Pages
│   ├── models.py             # SQLAlchemy DB schemas for User, Booking, Menu, Waste, Feedback
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── forms.py          # WTForms for Login & Register
│   │   └── routes.py         # Login, Register, Logout routes & decorators
│   ├── student/
│   │   ├── __init__.py
│   │   └── routes.py         # Student dashboard, booking, feedback routes
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── forms.py          # WTForms for Menu & Food Waste
│   │   └── routes.py         # Admin dashboard, Menu CRUD, Waste CRUD, Feedback views
│   ├── analytics/
│   │   ├── __init__.py
│   │   └── routes.py         # Analytics dashboard & CSV exports routes
│   ├── services/
│   │   ├── __init__.py
│   │   ├── booking_service.py   # Centralized deadline calculations
│   │   ├── analytics_service.py # Database aggregations for charts
│   │   └── report_service.py    # CSV generation logic using python csv module
│   ├── templates/            # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── auth/
│   │   ├── student/
│   │   ├── admin/
│   │   ├── analytics/
│   │   └── errors/
│   └── static/
│       ├── css/
│       │   └── style.css     # Clean modern CSS styling variables & accents
│       └── js/
│           └── charts.js     # Chart.js frontend canvas drawings
├── scripts/
│   └── seed_data.py          # Database resetting and mock-data seeding script
├── tests/
│   ├── conftest.py           # Pytest in-memory DB setups & client fixtures
│   ├── test_auth.py
│   ├── test_access_control.py
│   ├── test_booking.py
│   └── test_food_waste.py
├── config.py                 # App configurations (DB Path, Deadlines)
├── run.py                    # Server startup script
├── requirements.txt          # Python dependencies
├── .env.example              # Configuration template
└── README.md                 # Project README
```

---

## 5. Database Schema
### User Table
- `id` (INT, Primary Key)
- `name` (VARCHAR, Student/Admin name)
- `email` (VARCHAR, Unique, indexed)
- `password_hash` (VARCHAR, Werkzeug hashed)
- `role` (VARCHAR, 'student' or 'admin')
- `created_at` (DATETIME)

### MealBooking Table
- `id` (INT, Primary Key)
- `user_id` (INT, Foreign Key -> User.id)
- `date` (DATE, Target meal date)
- `meal_type` (VARCHAR, 'breakfast' | 'lunch' | 'dinner')
- `status` (VARCHAR, 'eating' | 'skipping')
- `created_at` (DATETIME)
- `updated_at` (DATETIME)
*Constraint*: Unique combination of `(user_id, date, meal_type)` enforced to prevent double bookings.

### Menu Table
- `id` (INT, Primary Key)
- `date` (DATE)
- `meal_type` (VARCHAR, 'breakfast' | 'lunch' | 'dinner')
- `items` (TEXT, Comma/newline separated menu list)
- `created_at` (DATETIME)
- `updated_at` (DATETIME)
*Constraint*: Unique combination of `(date, meal_type)` enforced.

### FoodWasteRecord Table
- `id` (INT, Primary Key)
- `date` (DATE)
- `meal_type` (VARCHAR, 'breakfast' | 'lunch' | 'dinner')
- `expected_students` (INT, Autocalculated from registered 'eating' students)
- `food_prepared` (FLOAT, in kg)
- `food_consumed` (FLOAT, in kg)
- `food_wasted` (FLOAT, in kg, derived as `prepared - consumed`)
- `created_at` (DATETIME)
*Constraint*: Unique combination of `(date, meal_type)` enforced.

### Feedback Table
- `id` (INT, Primary Key)
- `user_id` (INT, Foreign Key -> User.id)
- `date` (DATE)
- `meal_type` (VARCHAR, 'breakfast' | 'lunch' | 'dinner')
- `rating` (INT, 1 to 5)
- `comment` (TEXT, optional suggestions)
- `created_at` (DATETIME)

---

## 6. Installation & Execution (Windows)
### Prerequisites
- Python 3 Installed
- VS Code (Recommended)

### Step 1: Clone or Copy Project Files
Place the project directory files in your local workspace.

### Step 2: Create a Virtual Environment
Open PowerShell inside the project directory and run:
```powershell
python -m venv venv
```

### Step 3: Configure Environment Variables
Create a `.env` file in the project root (or export the variable in your shell) with a secret key:
```powershell
$env:SECRET_KEY="replace-this-with-a-long-random-string"
```
The app requires `SECRET_KEY` to start.

### Step 4: Activate the Virtual Environment
```powershell
.\venv\Scripts\activate
```

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Initialize the Database
Run the custom CLI command to generate database tables:
```powershell
flask init-db
```

### Step 6: Generate Seed Demo Data
Run the seeding script to populate users, menus, bookings, waste records, and feedback for testing:
```powershell
python scripts/seed_data.py
```

### Step 7: Start the Server
```powershell
python run.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 7. Demo Credentials
The seeding script generates the following credentials:

### Admin Credentials
- **Email**: `admin@college.edu`
- **Password**: `admin123`

### Student Credentials
- **Emails**: `student1@college.edu` through `student10@college.edu`
- **Password**: `student123` (same for all students)

---

## 8. Running Tests
Run the automated Pytest suite:
```powershell
.\venv\Scripts\python -m pytest
```

---

## 9. Security Features
1. **Password Hashing**: Done securely using Werkzeug's `scrypt` hashing implementation.
2. **Session Security**: Session tokens managed by Flask-Login and protected against hijacking.
3. **CSRF Protection**: Integrated via `Flask-WTF` across all data modifying POST routes.
4. **Backend Authorization Guards**: Access to student and admin blueprints is validated on the backend via decorators (`@admin_required` and `@student_required`). Hiding front-end buttons is NOT used as security.
5. **Strict Deadline Enforcement**: Checked on Flask routes. Front-end disables buttons, but sending manual POST requests past deadlines is rejected by backend datetime validations.

---

## 10. Known Limitations & Future Scope
- **Server Timezone Assumption**: The system assumes the hosting server's local timezone for deadline checks.
- **Production Improvement**: Implement timezone-aware UTC datetime fields in the database and convert to student's local timezone on client-side.
- **Biometric / QR Scanning**: Integrate QR-based student check-in at the dining hall entrance to track actual attendance vs booked eating slots.
