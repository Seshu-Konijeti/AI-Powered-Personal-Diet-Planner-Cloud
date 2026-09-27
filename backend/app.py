"""
Application entry point — REST API layer (Application Layer of the architecture).

Run locally:
    python backend/app.py
Runs on http://localhost:5000
"""
import os
import sys
from datetime import timedelta

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Allow `python backend/app.py` to resolve top-level packages (ai_engine, cloud)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

from backend.models.models import db
from backend.routes.auth import auth_bp, JWT_BLOCKLIST
from backend.routes.profile import profile_bp
from backend.routes.plans import plans_bp
from backend.routes.files import files_bp


def create_app():
    app = Flask(__name__)

    # ---- Configuration (from environment variables — never hardcoded) ----
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///diet_planner.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)
    app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024  # 6 MB hard cap on request size

    # CORS: allow the frontend origin to call this API
    CORS(app, resources={r"/*": {"origins": os.getenv("CORS_ORIGIN", "*")}})

    db.init_app(app)
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload["jti"] in JWT_BLOCKLIST

    @jwt.unauthorized_loader
    def missing_token_callback(reason):
        return jsonify({"error": "Missing or invalid authentication token."}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"error": "Invalid authentication token."}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Session expired, please log in again."}), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has been revoked, please log in again."}), 401

    # ---- Register API routes ----
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(plans_bp)
    app.register_blueprint(files_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "ai-diet-planner-cloud-api"}), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error."}), 500

    with app.app_context():
        db.create_all()  # creates tables if they do not exist yet (local/dev convenience)

    return app


app = create_app()

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=debug_mode)
