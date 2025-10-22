"""Flask-WTF forms for the To-Do app.
All comments are in English by requirement.
"""
from __future__ import annotations

from datetime import date
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DateField
from wtforms.validators import DataRequired, Length, Email, NumberRange, Optional
from flask_wtf import FlaskForm


class SignupForm(FlaskForm):
    """User registration form."""
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Create account')


class LoginForm(FlaskForm):
    """User login form."""
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class TaskForm(FlaskForm):
    """Task creation form."""
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=200)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=5000)])
    due_date = DateField('Due date', validators=[Optional()], format='%Y-%m-%d')
    priority = IntegerField('Priority (1=High, 5=Low)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Save task')
