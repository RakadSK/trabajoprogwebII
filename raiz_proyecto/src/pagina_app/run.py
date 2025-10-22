"""Application entry point and route definitions.
All inline comments must be in English (project requirement).
"""
from __future__ import annotations

import os
from urllib.parse import urlparse

from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

from .models import db, User, Task
from .forms import SignupForm, LoginForm, TaskForm


def create_app() -> Flask:
    """Application factory: configures Flask, extensions, and blueprints."""
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static',
    )

    # ----- Configuration -----
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'postgresql+psycopg://postgres:postgres@localhost:5432/todo_db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        # Flask-Login passes a str id; we cast to int for our PK.
        try:
            return User.get_by_id(int(user_id))
        except (TypeError, ValueError):
            return None

    # Create tables on first run (for demo/dev). In production use migrations.
    with app.app_context():
        db.create_all()

    # ----- Routes -----
    @app.route('/')
    def index():
        tasks = Task.get_all()
        return render_template('index.html', tasks=tasks)

    @app.route('/task/<string:slug>/')
    def task_detail(slug: str):
        task = Task.get_by_slug(slug)
        if not task:
            abort(404)
        return render_template('task_view.html', task=task)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # Redirect authenticated users away from login
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        form = LoginForm()
        if form.validate_on_submit():
            user = User.get_by_email(form.email.data.strip().lower())
            if not user or not user.check_password(form.password.data):
                flash('Invalid credentials', 'error')
                return render_template('login_form.html', form=form)

            login_user(user, remember=form.remember_me.data)

            # Secure handling of "next" to prevent open redirects
            next_url = request.args.get('next')
            if next_url:
                parsed = urlparse(next_url)
                if not parsed.netloc and not parsed.scheme:
                    return redirect(next_url)
            return redirect(url_for('index'))
        return render_template('login_form.html', form=form)

    @app.route('/signup/', methods=['GET', 'POST'])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        form = SignupForm()
        if form.validate_on_submit():
            existing = User.get_by_email(form.email.data.strip().lower())
            if existing:
                flash('Email is already registered', 'error')
                return render_template('admin/signup_form.html', form=form)

            user = User(
                name=form.name.data.strip(),
                email=form.email.data.strip().lower(),
            )
            user.set_password(form.password.data)
            user.save()

            login_user(user)
            flash('Welcome! Your account has been created.', 'success')
            return redirect(url_for('index'))
        return render_template('admin/signup_form.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/admin/task/', methods=['GET', 'POST'])
    @login_required
    def create_task():
        form = TaskForm(priority=3)
        if form.validate_on_submit():
            task = Task(
                user_id=current_user.id,
                title=form.title.data.strip(),
                description=form.description.data,
                due_date=form.due_date.data,
                priority=form.priority.data,
            )
            task.save()
            flash('Task created successfully', 'success')
            return redirect(task.public_url())
        return render_template('admin/task_form.html', form=form)

    # Custom error handlers
    @app.errorhandler(404)
    def not_found(error):  # noqa: ARG001 - signature mandated by Flask
        return render_template('404.html'), 404

    return app


# Allow `python -m todo_app.run`
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
