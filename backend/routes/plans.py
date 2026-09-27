"""Diet plan routes — AI generation + cloud-database-backed persistence."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from cloud import database_service as db_service
from ai_engine.diet_engine import generate_plan

plans_bp = Blueprint("plans", __name__)


@plans_bp.post("/generate-plan")
@jwt_required()
def generate_plan_route():
    user_id = int(get_jwt_identity())
    user = db_service.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    data = request.get_json(silent=True) or {}
    # Allow overriding profile values per-request, else fall back to saved profile
    dietary_preference = data.get("dietary_preference") or user.dietary_preference
    activity_level = data.get("activity_level") or user.activity_level
    goal = data.get("goal") or user.goal
    allergies = data.get("allergies") or user.allergies

    if not dietary_preference or not goal:
        return jsonify({
            "error": "dietary_preference and goal are required "
                     "(set them in your profile or pass them in this request)."
        }), 400

    plan_data, source = generate_plan(dietary_preference, activity_level, goal, allergies)
    plan = db_service.save_diet_plan(user_id, plan_data, source=source)

    return jsonify({"message": "Plan generated and saved.", "plan": plan.to_dict()}), 201


@plans_bp.get("/plans")
@jwt_required()
def list_plans():
    user_id = int(get_jwt_identity())
    plans = db_service.get_plans_for_user(user_id)
    return jsonify({"plans": [p.to_dict() for p in plans]}), 200


@plans_bp.get("/plans/<int:plan_id>")
@jwt_required()
def get_plan(plan_id):
    user_id = int(get_jwt_identity())
    plan = db_service.get_plan_by_id_for_user(plan_id, user_id)
    if not plan:
        # Same response whether it doesn't exist or belongs to another user —
        # prevents leaking which plan IDs exist (avoids user-enumeration/IDOR).
        return jsonify({"error": "Plan not found."}), 404
    return jsonify(plan.to_dict()), 200


@plans_bp.delete("/plans/<int:plan_id>")
@jwt_required()
def delete_plan_route(plan_id):
    user_id = int(get_jwt_identity())
    plan = db_service.get_plan_by_id_for_user(plan_id, user_id)
    if not plan:
        return jsonify({"error": "Plan not found."}), 404
    db_service.delete_plan(plan)
    return jsonify({"message": "Plan deleted."}), 200
