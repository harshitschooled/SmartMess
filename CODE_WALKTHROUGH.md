# SmartMess Code Walkthrough Guide

This document provides a folder-by-folder and file-by-file explanation of the SmartMess codebase. It is designed to help you explain the inner workings of the code during technical walkthroughs.

---

## 1. Project Directory Structure & Manifest

- **`run.py`**: Boots the Flask server.
- **`config.py`**: Defines configurations like DB paths and deadline times.
- **`requirements.txt`**: Specifies packages (Flask, SQLAlchemy, Login, WTForms, Pytest, Dotenv).
- **`app/`**: Core application package.
  - **`__init__.py`**: Contains the Application Factory (`create_app`).
  - **`models.py`**: Declares database schemas (User, MealBooking, Menu, FoodWasteRecord, Feedback).
  - **`auth/`**: Authentication controllers.
    - **`forms.py`**: Login/Register WTForms.
    - **`routes.py`**: Controllers for signing in/out and authorization decorators.
  - **`student/`**: Student routes (dashboard, booking, feedback).
  - **`admin/`**: Menu CRUD and waste logging controllers.
  - **`analytics/`**: Charts dashboard and report export routes.
  - **`services/`**: Isolated core helper functions (Time checks, Chart aggregates, CSV compilation).
  - **`templates/`**: HTML views grouped by user roles and blueprints.
  - **`static/`**: Stylesheet variables and front-end Chart.js bindings.
- **`scripts/`**: Seed scripts.
- **`tests/`**: Unit and integration test files.

---

## 2. Core Python Files Analysis

### `app/models.py`
- **Purpose**: Defines SQLAlchemy ORM database models.
- **Key Models**:
  - `User`: Handles accounts. Has relationships with bookings and feedback.
  - `MealBooking`: Enforces a unique constraint on `(user_id, date, meal_type)`.
  - `FoodWasteRecord`: Uses a property decorator (`waste_percentage`) to auto-derive waste efficiency.
  - `Menu` & `Feedback`: Stores menu items and rating scales.
- **Database Interactions**: Creation of tables via SQL schemas.

### `app/services/booking_service.py`
- **Purpose**: Centralizes date checks and booking deadlines.
- **Important Functions**:
  - `get_current_time()`: Returns current system time (or mocked test time).
  - `get_deadline_for_meal(date_val, meal_type)`: Combines target date and configuration time strings.
  - `is_booking_open(date_val, meal_type)`: Compares current time to meal deadline.
- **Input**: Date value (date or string), meal type ('breakfast' | 'lunch' | 'dinner').
- **Processing**: Calendar time calculations and configuration reading.
- **Output**: Boolean state or datetime deadline.

### `app/services/analytics_service.py`
- **Purpose**: Computes metrics and aggregates for Chart.js.
- **Important Functions**:
  - `get_analytics_data()`: Performs group-by queries on bookings, feedbacks, and waste logs.
- **Database Interactions**: Queries `func.avg(Feedback.rating)`, counts bookings grouped by status/date.
- **Output**: Dict containing date lists and count arrays structured for chart injection.

### `app/services/report_service.py`
- **Purpose**: Assembles data tables into CSV format.
- **Important Functions**:
  - `generate_bookings_csv(stream)`, `generate_waste_csv(stream)`, `generate_feedback_csv(stream)`
- **Input**: Python `StringIO` text buffer.
- **Processing**: Loops through SQL queries and writes rows using the standard `csv.writer`.
- **Output**: Writes structured CSV text into the provided buffer.

### `app/auth/routes.py`
- **Purpose**: Manages user login, signup, logout, and route access restriction.
- **Important Decorators**:
  - `@admin_required`: Restricts routes to administrators.
  - `@student_required`: Restricts routes to students.
- **Database Interactions**: Creates student records, checks password hash matching.
- **Routes**: `/auth/register`, `/auth/login`, `/auth/logout`.

---

## 3. Detailed Walkthrough of Key Flows

### Flow 1: User Registration
1. Student accesses `/auth/register` (GET) and receives the WTForm input page.
2. Student submits form details (POST).
3. The route `register()` parses the form and validates inputs (WTForms checks name length, email syntax, and matching passwords).
4. A database query checks if the email is already registered. If yes, it raises a validation error.
5. If valid, the password is hashed: `user.set_password(password)`.
6. A new `User` instance with role `'student'` is saved to the SQLite database.
7. The browser is redirected to `/auth/login` (GET) with a success message.

### Flow 2: User Login
1. User submits email and password on `/auth/login` (POST).
2. The route `login()` queries the database: `User.query.filter_by(email=email).first()`.
3. If found, `user.check_password(password)` checks the hashed password.
4. If valid, `login_user(user)` stores the user ID in the session.
5. Flask checks the user's role:
   - If `'admin'`, redirects to `/admin/dashboard`.
   - If `'student'`, redirects to `/student/dashboard`.

### Flow 3: Student Meal Booking
1. Student clicks "Eat" or "Skip" on `/student/dashboard`.
2. A form makes a POST request to `/student/book` with `date`, `meal_type`, and `status`.
3. The route calls `booking_service.is_booking_open()` to check deadlines on the server.
4. If past deadline, the booking is rejected, a error is flashed, and it redirects.
5. If open, the database is queried:
   - If booking exists: status is updated.
   - If booking doesn't exist: a new record is created.
6. The database commits the change, and the page redirects to the dashboard.

### Flow 4: Admin Menu Creation
1. Admin visits `/admin/menu/new` (GET).
2. Form is submitted with `date`, `meal_type`, and `items` (POST).
3. The route checks if a menu already exists for that date and meal type. If yes, it raises a validation error to prevent duplicates.
4. If unique, the `Menu` record is written to the database.
5. Redirects to `/admin/menus`.

### Flow 5: Food Waste Recording
1. Admin visits `/admin/waste/new` (GET).
2. Admin inputs the date, meal type, food prepared, and food consumed (in kg).
3. The route queries the number of student bookings with status `'eating'` for that date and meal type to set `expected_students`.
4. Backend validation checks:
   - Values are non-negative.
   - `food_consumed <= food_prepared`.
5. If valid, `food_wasted = food_prepared - food_consumed` is derived.
6. The record is written to the database, and the user is redirected to `/admin/waste`.

### Flow 6: Analytics Dashboard Generation
1. Admin visits `/analytics/dashboard`.
2. The controller calls `analytics_service.get_analytics_data()`.
3. The service runs queries to get trends and averages (waste trends, choice ratios, meal ratings).
4. The dictionary of arrays is converted to JSON in the template.
5. Chart.js reads the JSON values on the client side and renders visual graphs on HTML `<canvas>` elements.

### Flow 7: CSV Report Generation
1. Admin clicks "Bookings", "Waste", or "Feedback" export links on `/analytics/dashboard`.
2. The browser calls the corresponding route: `/analytics/export/bookings`, `/analytics/export/waste`, or `/analytics/export/feedback`.
3. The route calls `report_service` functions, passing a `StringIO` buffer.
4. The service fetches database records, formatting them into CSV rows.
5. The route wraps the CSV data in a Flask `Response` with headers:
   - `Content-Type: text/csv`
   - `Content-Disposition: attachment; filename=report_name.csv`
6. The browser downloads the CSV file directly to the client's machine.
