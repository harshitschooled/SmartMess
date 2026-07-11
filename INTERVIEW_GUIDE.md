# SmartMess Technical Interview Guide

This guide is designed to help you explain the architecture, design choices, database schema, security features, and technical details of the **SmartMess** system during technical job interviews.

---

## 1. Project Summaries & High-Level Design

### The Project in 30 Seconds
SmartMess is a web application designed to reduce food wastage in college messes. It works by having students confirm whether they will eat or skip a meal (breakfast, lunch, dinner) before a set deadline. Using these bookings, mess admins get exact attendance projections, enabling them to prepare correct amounts of food. Admins also track daily waste in kilograms, collect student feedback, and analyze food consumption trends using dynamic Chart.js dashboards.

### The Project in 2 Minutes
"As a final-year student, I built SmartMess to solve a real-world logistics problem: college mess kitchens prepare food for thousands of students daily based on rough estimates, leading to heavy food wastage.

I chose a lightweight Python stack using Flask, SQLAlchemy, SQLite, and Bootstrap 5. Students register and log in to a dashboard where they view today's menu and confirm their eating or skipping choice. The system enforces strict deadlines—like closing breakfast bookings at 9 PM on the previous day. 

For administrators, the app aggregates student choices into expected attendance figures. Admins log actual food prepared and consumed in kilograms, and the system automatically calculates wasted food and waste percentages. There's also a feedback system where students rate meals, and an analytics page rendering visual trends via Chart.js.

I structured the project using professional design principles like the **Application Factory pattern** and **Blueprints** to keep components modular. I also built a comprehensive automated test suite with **Pytest** running against an in-memory database to verify authentication, role access control, and deadline validation."

---

## 2. Core Technical Concepts

### 3. The Problem Being Solved
Kitchen operations suffer from a lack of demand forecasting. SmartMess replaces estimation with a direct declaration model, shifting the mess from a "push" supply model to a "pull" demand-driven model.

### 4. Why Flask was Chosen
Flask was chosen because:
- **Micro-framework flexibility**: It does not force developer decisions (unlike Django), allowing us to understand and explain every line of imported configuration.
- **Speed of development**: It is lightweight and easy to run locally on Windows using VS Code.
- **Server-Side Rendering (SSR)**: Perfect for SEO, security, and simpler beginner-friendly architectures compared to complex React/Node.js SPA setups.

### 5. Application Architecture
The project follows a modular Model-View-Controller (MVC) style:
- **Models**: SQLAlchemy database classes in `app/models.py`.
- **Views**: Jinja2 templates styled with Bootstrap 5.
- **Controllers**: Flask Blueprint routes which handle incoming client requests, orchestrate business logic, and return responses.
- **Services**: Dedicated business logic helpers (like deadline math, aggregations, and CSV compilation) separated from routes.

### 6. Flask Application Factory Pattern
Implemented via `create_app()` in `app/__init__.py`. This function creates the Flask application instance, registers configurations, binds database structures, registers blueprints, and hooks error pages. 
*Interview benefit*: Explain how this prevents global state mutability issues and makes testing easy by spinning up separate app instances with test configs.

### 7. Flask Blueprints
We split routes into distinct business areas (blueprints): `auth`, `student`, `admin`, and `analytics`. This ensures separation of concerns.

### 8. Request-Response Lifecycle Example (Meal Booking)
1. Student clicks "Eat" on the student dashboard.
2. Browser sends a secure HTTP POST request to `/student/book` with form data: `date`, `meal_type`, `status`, and `csrf_token`.
3. Flask CSRF extension interceptor validates the token.
4. The request reaches `book()` in `app/student/routes.py`.
5. The route calls `booking_service.is_booking_open()` to verify if the deadline has passed.
6. If open, the route runs a create-or-update query in SQLite via SQLAlchemy.
7. The database commits the transaction.
8. Flask flashes a success message and returns a `302 Redirect` header pointing to `/student/dashboard`.
9. The browser requests `/student/dashboard` (GET), and the server renders the dashboard with the updated status and flash message.

### 9. Database Tables & Relationships
- **User** has a one-to-many relationship with **MealBooking** and **Feedback**.
- **MealBooking** links back to **User** via `user_id` foreign key.
- **Feedback** links back to **User** via `user_id` foreign key.
- Cascading deletes are enabled: deleting a user deletes all their bookings and feedback to prevent orphaned records.

### 10. Authentication Flow
Managed via **Flask-Login**:
1. User enters email and password on `/auth/login`.
2. Flask queries the user in the database.
3. Password verified using `werkzeug.security.check_password_hash`.
4. If valid, `login_user(user)` is called, which creates a secure session cookie in the user's browser.
5. On subsequent requests, Flask-Login reads the cookie and loads the user object via `@login_manager.user_loader`.

### 11. Password Hashing
We never store plain-text passwords. We use `generate_password_hash` which implements secure hashing algorithms (scrypt) with automatic salting.

### 12. Session-Based Authentication
Flask sessions use a cryptographically signed cookie stored client-side. The signature is checked against the server's `SECRET_KEY`. If tampered with, the session is invalidated.

### 13. Role-Based Authorization
We implemented custom route decorators: `@student_required` and `@admin_required`. These decorators verify if `current_user.role` matches the expected role. If unauthorized, they trigger `abort(403)`.
*Critical Note*: Frontend navigation links are hidden, but backend routes validate the role as the primary security layer.

### 14. Meal Booking Create-or-Update Logic
To prevent duplicate records for a student on a specific day/meal:
- We check if a record with the combination `(user_id, date, meal_type)` already exists in the database.
- If it exists, we update the status (`eating` -> `skipping` or vice versa) and the `updated_at` timestamp.
- If it does not exist, we create a new `MealBooking` instance.

### 15. Unique Database Constraints
To prevent race conditions, the SQLite database enforces constraints:
- `UniqueConstraint('user_id', 'date', 'meal_type')` on `MealBooking`.
- `UniqueConstraint('date', 'meal_type')` on `Menu` and `FoodWasteRecord`.

### 16. Booking Deadline Calculation
Calculations are centralized in `app/services/booking_service.py`:
- Target date and meal type determine the deadline.
- E.g., for Tomorrow's Breakfast: deadline is `date - 1 day` at `21:00`.
- We construct a datetime object from config values and compare it against `get_current_time()`.

### 17. Server-Side Validation
Form entries are parsed by WTForms which validates data types, email formats, and checks password matching. 

### 18. Menu Management CRUD Operations
Admin routes handle standard CRUD. A menu is stored with items as a text block mapped to `(date, meal_type)`. If an admin edits a menu, we update the corresponding record.

### 19. SQLAlchemy Queries for Dashboard Statistics
- Expected attendance: `MealBooking.query.filter_by(date=today, status='eating').count()`
- Active student count: `User.query.filter_by(role='student').count()`

### 20. How Analytics are Calculated
Calculated via `analytics_service.py`:
- Daily attendance: grouped queries counting choices over time.
- Average rating: `func.avg(Feedback.rating)`.
- Most skipped meal: counts of `status='skipping'` grouped by `meal_type` to find the maximum.

### 21. How CSV Reports are Generated
The `report_service.py` uses the standard Python `csv` library. It streams database records directly into an in-memory text buffer (`StringIO`) and returns a Flask `Response` with `text/csv` mime type. This avoids writing files to disk.

### 22. Testing Approach
We use **Pytest** with mock fixtures:
- Database: setup in `conftest.py` with `sqlite:///:memory:` to isolate tests.
- CSRF is disabled in tests to allow mock POST requests.
- Datetime is mocked via `booking_service.set_test_time()` to test deadline enforcement.

### 23. Security Measures
Includes CSRF tokens, hashed passwords, session checks, backend role verification, and sanitizing user inputs.

### 24. Project Limitations
- **Server Timezone**: Relies on host environment timezone.
- **SQLite Concurrency**: SQLite locks the database on writes, limiting high concurrent operations.
- **Self-Reported Waste**: Admins enter consumption manually, which is prone to human error.

### 25. Future Improvements
- **Timezone-aware UTC storage**: Save all datetimes in UTC and convert to client timezone.
- **RFID/QR Code Integration**: Scan student IDs at the food counter to compare actual consumption against bookings.

---

## 3. 30 Interview Questions & Answers

#### Q1: What is the main goal of the SmartMess project?
**A**: To reduce college mess food waste by requiring students to confirm their meal attendance beforehand, allowing kitchens to cook exact portions.

#### Q2: Why did you use the Flask Application Factory pattern?
**A**: It allows us to instantiate multiple applications dynamically with different configurations (like a testing config with an in-memory database and a development config).

#### Q3: How do you prevent a student from registering as an Admin?
**A**: The registration form and route only permit creating users with the `student` role. Admin accounts can only be created via backend seed scripts or CLI commands.

#### Q4: How is session-based authentication implemented?
**A**: We use Flask-Login which sets a cryptographically signed cookie in the browser. When requests come in, Flask-Login verifies the cookie against the server's secret key.

#### Q5: How did you implement password security?
**A**: By hashing passwords using `werkzeug.security.generate_password_hash` with scrypt salting, and validating them using `check_password_hash`.

#### Q6: Explain your custom decorators `@student_required` and `@admin_required`.
**A**: They wrap route functions, check if the logged-in user's role matches the requirements, and call `abort(403)` if there is a mismatch.

#### Q7: Why are frontend button disabling tricks not enough for security?
**A**: Anyone can inspect elements to enable buttons, or make direct HTTP POST requests using tools like Postman. Backend authentication and validation are mandatory.

#### Q8: How is the create-or-update logic handled for meal bookings?
**A**: We query if a booking exists for the user on that date and meal. If yes, we edit the status; if no, we insert a new record.

#### Q9: What happens if a student tries to book a meal past the deadline?
**A**: The backend `book()` route checks if the current time exceeds the deadline. If it does, the booking is rejected, and a danger flash message is shown.

#### Q10: How do you check deadlines in tests without changing the system clock?
**A**: I created a helper `get_current_time()` in the booking service. In tests, I override this with a setter function to mock different times.

#### Q11: What timezone does your application assume?
**A**: The system assumes the local time of the hosting environment.

#### Q12: How would you fix the timezone issue for production?
**A**: By storing all database timestamps in UTC and using JavaScript on the frontend to calculate deadlines relative to the client's browser timezone.

#### Q13: How is food waste calculated in your application?
**A**: The admin logs the prepared and consumed food in kilograms. The model auto-derives: `food_wasted = food_prepared - food_consumed`.

#### Q14: How is waste percentage calculated? What about division by zero?
**A**: `(food_wasted / food_prepared) * 100`. The model property checks if `food_prepared > 0` before dividing; if not, it returns `0.0`.

#### Q15: What validations are performed when saving a food waste record?
**A**: We validate that values are non-negative, and that `food_consumed` does not exceed `food_prepared`.

#### Q16: How do you show expected attendance on the admin dashboard?
**A**: By querying the count of bookings for today where `status == 'eating'`.

#### Q17: Why did you choose SQLite?
**A**: SQLite requires zero installation/configuration, stores data in a single file, and is perfect for local Windows development and portfolios.

#### Q18: What is a database unique constraint and why is it important here?
**A**: It prevents duplicate rows at the database level. For example, a student cannot have two different booking rows for the same date and meal type.

#### Q19: How did you implement CSRF protection?
**A**: By using the `Flask-WTF` extension. It inserts a hidden CSRF token into form templates and validates it on every POST request.

#### Q20: How are CSV reports generated?
**A**: Using Python's built-in `csv` module and `io.StringIO`. The database records are written to an in-memory buffer and returned as a downloadable response.

#### Q21: Why not use Pandas for CSV generation?
**A**: Pandas is a heavy library designed for data science. For simple table exports, Python's built-in `csv` module is faster, lighter, and keeps requirements minimal.

#### Q22: What are the three custom error pages you created?
**A**: 403 Forbidden (authorization failure), 404 Not Found (missing resources), and 500 Internal Server Error (exceptions).

#### Q23: How do you handle database sessions on a 500 error?
**A**: The error handler rolls back the session (`db.session.rollback()`) to prevent dirty transactions from corrupting the database state.

#### Q24: How does Pytest isolate tests from the development database?
**A**: In `conftest.py`, the test config sets `SQLALCHEMY_DATABASE_URI` to `sqlite:///:memory:`, creating a temporary database in RAM that deletes itself after tests run.

#### Q25: Why is the seed script idempotent?
**A**: It drops all database tables and recreate them (`db.drop_all()`, `db.create_all()`) before writing mock data, preventing duplicate records if run twice.

#### Q26: How does Chart.js render graphs in your application?
**A**: Jinja2 serializes the database aggregates to JSON. Frontend JavaScript reads this data and renders charts onto HTML5 `<canvas>` elements.

#### Q27: How does database cascading delete work in this project?
**A**: The User model defines relationships with `cascade="all, delete-orphan"`. If a user is deleted, all their bookings and feedbacks are deleted automatically.

#### Q28: How do you enforce data types on input forms?
**A**: Using WTForms validation fields like `DecimalField`, `DateField`, and validators like `NumberRange`.

#### Q29: What is the benefit of keeping business logic out of route files?
**A**: It makes route files highly readable, simplifies code maintenance, and allows us to reuse business rules (like deadline checks) across routes and CLI commands.

#### Q30: What did you learn while building this project?
**A**: I learned how to structure a production-ready Flask application using design patterns, implement backend security layers, and test complex logic like date deadlines.
