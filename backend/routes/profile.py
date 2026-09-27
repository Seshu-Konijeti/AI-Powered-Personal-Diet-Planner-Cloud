"""Profile routes — protected, user can only ever read/edit their own profile."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from cloud import database_service as db_service

profile_bp = Blueprint("profile", __name__)


@profile_bp.get("/profile")
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = db_service.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify(user.to_public_dict()), 200


@profile_bp.put("/profile")
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = db_service.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    data = request.get_json(silent=True) or {}
    allowed_fields = {
        "age", "height_cm", "weight_kg", "activity_level",
        "dietary_preference", "goal", "allergies", "name",
    }
    updates = {k: v for k, v in data.items() if k in allowed_fields}

    user = db_service.update_user_profile(user, updates)
    return jsonify({"message": "Profile updated.", "user": user.to_public_dict()}), 200
