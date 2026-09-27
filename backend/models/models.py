"""
Database models — represents the Cloud Database (Data Layer) of the architecture.
Uses SQLAlchemy ORM so the same models can point at SQLite (local/free-tier)
or a managed cloud database (Postgres on RDS/Cloud SQL, etc.) by only
changing the DATABASE_URL environment variable — no code changes needed.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    age = db.Column(db.Integer, nullable=True)
    height_cm = db.Column(db.Float, nullable=True)
    weight_kg = db.Column(db.Float, nullable=True)
    activity_level = db.Column(db.String(30), nullable=True)  # sedentary/light/moderate/active
    dietary_preference = db.Column(db.String(30), nullable=True)  # vegetarian/vegan/non_vegetarian
    goal = db.Column(db.String(40), nullable=True)  # balanced/weight_management/fitness
    allergies = db.Column(db.String(255), nullable=True)  # optional, comma separated demo field

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    plans = db.relationship("DietPlan", backref="user", cascade="all, delete-orphan")
    files = db.relationship("UserFile", backref="user", cascade="all, delete-orphan")

    def to_public_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "age": self.age,
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg,
            "activity_level": self.activity_level,
            "dietary_preference": self.dietary_preference,
            "goal": self.goal,
            "allergies": self.allergies,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DietPlan(db.Model):
    __tablename__ = "diet_plans"

    plan_id = db.Column(db.Integer, primary_key=True)
    # Foreign key -> demonstrates user-specific data isolation at the DB layer
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)

    breakfast = db.Column(db.Text, nullable=False)
    lunch = db.Column(db.Text, nullable=False)
    snack = db.Column(db.Text, nullable=False)
    dinner = db.Column(db.Text, nullable=False)
    nutrition_summary = db.Column(db.Text, nullable=False)  # JSON string
    hydration_reminder = db.Column(db.String(255), nullable=True)
    source = db.Column(db.String(20), default="rule_based")  # rule_based | ai_api

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            "plan_id": self.plan_id,
            "user_id": self.user_id,
            "breakfast": self.breakfast,
            "lunch": self.lunch,
            "snack": self.snack,
            "dinner": self.dinner,
            "nutrition_summary": json.loads(self.nutrition_summary),
            "hydration_reminder": self.hydration_reminder,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "disclaimer": "Educational / general wellness example only. Not medical or clinical nutrition advice.",
        }


class UserFile(db.Model):
    __tablename__ = "user_files"

    file_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)

    filename = db.Column(db.String(255), nullable=False)
    storage_path = db.Column(db.String(500), nullable=False)  # object storage "key"
    content_type = db.Column(db.String(100), nullable=True)
    size_bytes = db.Column(db.Integer, nullable=True)

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "file_id": self.file_id,
            "user_id": self.user_id,
            "filename": self.filename,
            "storage_path": self.storage_path,
            "content_type": self.content_type,
            "size_bytes": self.size_bytes,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }
