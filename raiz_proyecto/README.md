# To-Do List App (Flask + PostgreSQL)

**What it is:** A minimal, secure To-Do list web application with user authentication, PostgreSQL persistence, and CRUD for a `Task` entity.

**Why:** Demonstrates a clean Flask stack with forms (Flask-WTF), session management (Flask-Login), ORM (Flask-SQLAlchemy), slug URLs, and basic templates.

## Tech Stack
- Python 3.12+
- Flask 3.1.2+
- Flask-WTF 1.2.2+
- Flask-Login 0.6.3+
- Flask-SQLAlchemy 3.1.1+
- PostgreSQL via `psycopg` 3.2.10+
- `python-slugify` 8.0.4+
- `email-validator` 2.3.0+

## Project Structure
```
./
├── pyproject.toml
├── README.md
├── src/
│   └── todo_app/
│       ├── run.py
│       ├── models.py
│       ├── forms.py
│       ├── static/
│       │   └── style.css
│       └── templates/
│           ├── base_template.html
│           ├── index.html
│           ├── task_view.html
│           ├── login_form.html
│           └── admin/
│               ├── signup_form.html
│               └── task_form.html
└── .gitignore
```

## Environment Variables
- `SECRET_KEY` – a cryptographically secure random string.
- `DATABASE_URL` – PostgreSQL DSN in the form `postgresql+psycopg://user:password@host:5432/dbname`.

> **Note:** Do **not** commit real secrets. Use your shell or a secrets manager.

## Database Setup
1. Create a PostgreSQL database and user, e.g. using `psql`:
   ```bash
   createdb todo_db
   # Or in psql: CREATE DATABASE todo_db;
   ```
2. Export the DSN, for example:
   ```bash
   export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/todo_db"
   export SECRET_KEY="replace-with-a-long-random-string"
   ```

## Installation (with Rye)
```bash
# If you do not have Rye: https://rye-up.com/ (install as per docs)
rye sync   # creates virtual env and installs dependencies
```

## Run the App
```bash
rye run start
# or
python -m todo_app.run
```
First run auto-creates tables. Visit `http://127.0.0.1:5000/`.

## Available Routes
- `GET /` – List all tasks (public)
- `GET /task/<slug>/` – Task detail (public)
- `GET|POST /login` – Login form
- `GET|POST /signup/` – User registration (auto-login)
- `GET /logout` – Logout
- `GET|POST /admin/task/` – Create task (requires login)

## Models
- `User(id, name, email, password_hash, ...)`
- `Task(id, user_id, title, description, due_date, priority, completed, slug)`

## Notes
- Passwords are hashed with Werkzeug.
- CSRF protection is enabled by Flask-WTF.
- Email validation uses `email-validator` via WTForms' `Email()` validator.
- Slugs are generated from the task title and deduplicated with numeric suffixes.

## Development Tips
- Run Flask with reloader: `FLASK_DEBUG=1 python -m todo_app.run`
- Use a separate database for development and production.
- Prefer a managed Postgres (e.g., Docker, Neon, Render) in deployment.

