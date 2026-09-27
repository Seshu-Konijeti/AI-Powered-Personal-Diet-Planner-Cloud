"""
Authentication routes — demonstrates Authentication (who you are) vs
Authorization (what you can access, enforced via @jwt_required + user_id scoping).
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity

from cloud import database_service as db_service
from backend.utils.security import (
    hash_password, verify_password, is_valid_email, is_valid_password,
)

auth_bp = Blueprint("auth", __name__)

# Simple in-memory JWT blocklist for logout (demo-appropriate; use Redis in production)
JWT_BLOCKLIST = set()


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not is_valid_email(email) or not is_valid_password(password):
        return jsonify({"error": "Provide a valid name, email, and password (min 8 characters)."}), 400

    if db_service.get_user_by_email(email):
        return jsonify({"error": "An account with this email already exists."}), 409

    user = db_service.create_user(name, email, hash_password(password))
    return jsonify({"message": "Registration successful.", "user": user.to_public_dict()}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = db_service.get_user_by_email(email)
    if not user or not verify_password(password, user.password_hash):
        return jsonify({"error": "Invalid email or password."}), 401

    token = create_access_token(identity=str(user.user_id))
    return jsonify({"message": "Login successful.", "access_token": token, "user": user.to_public_dict()}), 200


@auth_bp.post("/logout")
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    JWT_BLOCKLIST.add(jti)
    return jsonify({"message": "Logged out successfully."}), 200
