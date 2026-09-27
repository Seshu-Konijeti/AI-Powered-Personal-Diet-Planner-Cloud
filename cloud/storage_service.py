"""
Cloud Object Storage Service (Storage Layer abstraction).

Cloud Database  -> structured, queryable records (users, plans, metadata).
Cloud Object Storage -> raw files/blobs (images, exports) addressed by a key/path.

This module simulates an object storage bucket using the local filesystem
(`storage_bucket/`), keyed exactly like a real bucket would be:
    user_<id>/<uuid>_<filename>

STORAGE_BACKEND env var controls which implementation is used:
    "local"    -> LocalStorageBackend (default, free, no setup)
    "s3"       -> stub showing exactly where boto3 (AWS S3) would plug in
    "firebase" -> stub showing exactly where Firebase/Supabase Storage would plug in

Swapping backends never requires touching route code — routes only call
`storage.save_file(...)`, `storage.delete_file(...)`, `storage.get_file_path(...)`.
"""
import os
import uuid


class LocalStorageBackend:
    """Simulates cloud object storage using the local filesystem."""

    def __init__(self, base_dir="storage_bucket"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def save_file(self, user_id, filename, file_stream) -> dict:
        user_dir = os.path.join(self.base_dir, f"user_{user_id}")
        os.makedirs(user_dir, exist_ok=True)

        unique_name = f"{uuid.uuid4().hex}_{filename}"
        storage_path = os.path.join(user_dir, unique_name)

        file_stream.save(storage_path)
        size_bytes = os.path.getsize(storage_path)

        return {"storage_path": storage_path, "size_bytes": size_bytes}

    def delete_file(self, storage_path: str) -> bool:
        try:
            if os.path.exists(storage_path):
                os.remove(storage_path)
            return True
        except OSError:
            return False

    def get_file_path(self, storage_path: str) -> str:
        return storage_path


class S3StorageBackend:
    """
    STUB — shows the swap-in point for AWS S3 (Option C / advanced cloud deployment).
    Uncomment and `pip install boto3` to activate. Never hardcode credentials —
    boto3 reads AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_REGION from env vars.
    """

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        # import boto3
        # self.client = boto3.client("s3")

    def save_file(self, user_id, filename, file_stream) -> dict:
        # key = f"user_{user_id}/{uuid.uuid4().hex}_{filename}"
        # self.client.upload_fileobj(file_stream, self.bucket_name, key)
        # size_bytes = file_stream.content_length
        # return {"storage_path": key, "size_bytes": size_bytes}
        raise NotImplementedError("Install boto3 and configure AWS credentials to enable S3 storage.")

    def delete_file(self, storage_path: str) -> bool:
        # self.client.delete_object(Bucket=self.bucket_name, Key=storage_path)
        raise NotImplementedError("Install boto3 and configure AWS credentials to enable S3 storage.")

    def get_file_path(self, storage_path: str) -> str:
        return f"https://{self.bucket_name}.s3.amazonaws.com/{storage_path}"


def get_storage_backend():
    backend = os.getenv("STORAGE_BACKEND", "local")
    if backend == "s3":
        return S3StorageBackend(bucket_name=os.getenv("S3_BUCKET_NAME", "diet-planner-bucket"))
    # Default: local simulation, zero cost, zero setup
    return LocalStorageBackend()


storage = get_storage_backend()
