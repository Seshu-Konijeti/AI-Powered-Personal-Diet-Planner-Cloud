"""File routes — demonstrates Cloud Object Storage separate from the Cloud Database."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from cloud import database_service as db_service
from cloud.storage_service import storage
from backend.utils.security import is_allowed_filename

files_bp = Blueprint("files", __name__)

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB demo limit


@files_bp.post("/upload")
@jwt_required()
def upload_file():
    user_id = int(get_jwt_identity())

    if "file" not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    uploaded = request.files["file"]
    if uploaded.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not is_allowed_filename(uploaded.filename):
        return jsonify({"error": "File type not allowed. Use png/jpg/jpeg/gif/pdf/txt."}), 400

    result = storage.save_file(user_id, uploaded.filename, uploaded)

    if result["size_bytes"] > MAX_FILE_SIZE_BYTES:
        storage.delete_file(result["storage_path"])
        return jsonify({"error": "File exceeds 5 MB demo limit."}), 400

    record = db_service.create_file_record(
        user_id=user_id,
        filename=uploaded.filename,
        storage_path=result["storage_path"],
        content_type=uploaded.content_type,
        size_bytes=result["size_bytes"],
    )
    return jsonify({"message": "File uploaded to cloud storage.", "file": record.to_dict()}), 201


@files_bp.get("/files")
@jwt_required()
def list_files():
    user_id = int(get_jwt_identity())
    files = db_service.get_files_for_user(user_id)
    return jsonify({"files": [f.to_dict() for f in files]}), 200


@files_bp.delete("/files/<int:file_id>")
@jwt_required()
def delete_file_route(file_id):
    user_id = int(get_jwt_identity())
    record = db_service.get_file_by_id_for_user(file_id, user_id)
    if not record:
        return jsonify({"error": "File not found."}), 404

    storage.delete_file(record.storage_path)
    db_service.delete_file_record(record)
    return jsonify({"message": "File deleted."}), 200
