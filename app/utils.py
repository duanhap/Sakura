from flask_login import current_user


def is_admin() -> bool:
    """Check if the current user is an admin."""
    return bool(current_user.is_authenticated and current_user.role == "ADMIN")
