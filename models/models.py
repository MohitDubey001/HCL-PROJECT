"""
DB Models
"""

import datetime
from flask_login import (
    UserMixin,
    LoginManager,
)
from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import JSON

db = SQLAlchemy()


# Models
class Respondent(db.Model):
    __tablename__ = "respondents"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(200), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    responses = db.relationship("Response", backref="respondent", lazy=True)


class Response(db.Model):
    __tablename__ = "responses"

    id = db.Column(db.Integer, primary_key=True)
    respondent_id = db.Column(
        db.Integer, db.ForeignKey("respondents.id"), nullable=True
    )
    submitted_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    answers = db.Column(JSON, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    interpretation = db.Column(db.String(200), nullable=False)
    flagged_suicidal_thoughts = db.Column(db.Boolean, nullable=False, default=False)


class Admin(UserMixin, db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Auth
login_manager = LoginManager()
login_manager.login_view = "main.admin_login"  # type: ignore


@login_manager.user_loader
def load_user(admin_id):
    return Admin.query.get(int(admin_id))


# Score computation
def interpret_phq9(score):
    """Interprets the PHQ9 score for the respondent."""
    if score <= 4:
        return "Minimal or none (0-4)"
    elif 5 <= score <= 9:
        return "Mild (5-9)"
    elif 10 <= score <= 14:
        return "Moderate (10-14)"
    elif 15 <= score <= 19:
        return "Moderately severe (15-19)"
    else:
        return "Severe (20-27)"
