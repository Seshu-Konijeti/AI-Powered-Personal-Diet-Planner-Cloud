"""
Security utilities — password hashing and input validation helpers.
Demonstrates: password security (never store plaintext), basic input validation.
"""
import re
import bcrypt


def hash_password(plain_password: str) -> str:
    """Hash a password with bcrypt (includes a per-password random salt)."""
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, AttributeError):
        return False


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email: str) -> bool:
    return bool(email) and bool(EMAIL_REGEX.match(email))


def is_valid_password(password: str) -> bool:
    """Basic demo rule: at least 8 characters. Extend for production use."""
    return bool(password) and len(password) >= 8


ALLOWED_UPLOAD_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "txt"}


def is_allowed_filename(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_UPLOAD_EXTENSIONS
