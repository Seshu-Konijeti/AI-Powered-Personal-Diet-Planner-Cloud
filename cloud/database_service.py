"""
Cloud Database Service (Data Layer abstraction).

In cloud computing, the application talks to the database through a service
layer instead of scattering raw queries everywhere. This makes it trivial to
swap SQLite (local/free) for a managed cloud database (AWS RDS, Google Cloud
SQL, Firestore, Supabase Postgres, ...) by changing DATABASE_URL only.

This module wraps SQLAlchemy session operations for Users, DietPlans and
UserFiles so routes never touch `db.session` directly.
"""
from backend.models.models import db, User, DietPlan, UserFile


# ---------- Users ----------

def create_user(name, email, password_hash):
    user = User(name=name, email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()
    return user


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def update_user_profile(user, fields: dict):
    for key, value in fields.items():
        if hasattr(user, key) and value is not None:
            setattr(user, key, value)
    db.session.commit()
    return user


# ---------- Diet Plans ----------

def save_diet_plan(user_id, plan_data: dict, source="rule_based"):
    import json
    plan = DietPlan(
        user_id=user_id,
        breakfast=plan_data["breakfast"],
        lunch=plan_data["lunch"],
        snack=plan_data["snack"],
        dinner=plan_data["dinner"],
        nutrition_summary=json.dumps(plan_data["nutrition_summary"]),
        hydration_reminder=plan_data.get("hydration_reminder"),
        source=source,
    )
    db.session.add(plan)
    db.session.commit()
    return plan


def get_plans_for_user(user_id):
    return DietPlan.query.filter_by(user_id=user_id).order_by(DietPlan.created_at.desc()).all()


def get_plan_by_id_for_user(plan_id, user_id):
    """Always scope by user_id too -> prevents cross-user data access (IDOR)."""
    return DietPlan.query.filter_by(plan_id=plan_id, user_id=user_id).first()


def delete_plan(plan):
    db.session.delete(plan)
    db.session.commit()


# ---------- Files (metadata only — bytes live in Object Storage) ----------

def create_file_record(user_id, filename, storage_path, content_type, size_bytes):
    file_record = UserFile(
        user_id=user_id,
        filename=filename,
        storage_path=storage_path,
        content_type=content_type,
        size_bytes=size_bytes,
    )
    db.session.add(file_record)
    db.session.commit()
    return file_record


def get_files_for_user(user_id):
    return UserFile.query.filter_by(user_id=user_id).order_by(UserFile.uploaded_at.desc()).all()


def get_file_by_id_for_user(file_id, user_id):
    return UserFile.query.filter_by(file_id=file_id, user_id=user_id).first()


def delete_file_record(file_record):
    db.session.delete(file_record)
    db.session.commit()
