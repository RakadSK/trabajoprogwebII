"""Database models for the To-Do app.
All comments are intentionally in English to meet the project requirement.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from slugify import slugify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import event

# SQLAlchemy instance (initialized in run.py)
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Application user model."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationship: one user -> many tasks
    tasks = db.relationship(
        'Task', backref='owner', lazy=True, cascade='all, delete-orphan'
    )

    # Flask-Login requires a str id for cookies if custom; default works.

    # ----- Authentication helpers -----
    def set_password(self, password: str) -> None:
        """Hash and store the password using Werkzeug."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify the given password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    # ----- Persistence helpers -----
    def save(self) -> None:
        """Persist the user in the database."""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(user_id: int) -> Optional['User']:
        """Fetch a user by primary key."""
        return db.session.get(User, user_id)

    @staticmethod
    def get_by_email(email: str) -> Optional['User']:
        """Fetch a user by email address."""
        return User.query.filter_by(email=email).first()


class Task(db.Model):
    """Task entity for the To-Do list domain."""
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.Integer, nullable=False, default=3)  # 1 (high) - 5 (low)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    slug = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def _generate_unique_slug(self) -> str:
        """Generate a unique slug from the task title.

        If the base slug already exists, append an incrementing suffix: -1, -2, ...
        """
        base = slugify(self.title)
        if not base:
            base = slugify(f"task-{self.id or ''}")
        slug_candidate = base
        counter = 1
        while Task.query.filter_by(slug=slug_candidate).first() is not None:
            slug_candidate = f"{base}-{counter}"
            counter += 1
        return slug_candidate

    def public_url(self) -> str:
        """Return the public URL path for this task."""
        return f"/task/{self.slug}/"

    def save(self) -> None:
        """Persist the task, generating slug and handling collisions."""
        if not self.slug:
            self.slug = self._generate_unique_slug()
        db.session.add(self)
        try:
            db.session.commit()
        except IntegrityError:
            # If another row just took the same slug, regenerate and retry once.
            db.session.rollback()
            self.slug = self._generate_unique_slug()
            db.session.add(self)
            db.session.commit()

    @staticmethod
    def get_by_slug(slug: str) -> Optional['Task']:
        """Fetch a task by its unique slug."""
        return Task.query.filter_by(slug=slug).first()

    @staticmethod
    def get_all():
        """Return all tasks ordered by creation date descending."""
        return Task.query.order_by(Task.created_at.desc()).all()


# Optional: ensure slug before insert if missing.
@event.listens_for(Task, 'before_insert')
def task_before_insert(mapper, connection, target: Task):
    if not target.slug:
        # This will still go through save's logic when called explicitly,
        # but for direct session.add/commit it guarantees a slug exists.
        base = slugify(target.title) or 'task'
        target.slug = base
