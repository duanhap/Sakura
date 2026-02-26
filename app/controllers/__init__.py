# Controllers package initialization
from app.controllers.auth_controller import auth_bp
from app.controllers.admin_controller import admin_bp
from app.controllers.user_controller import user_bp
from app.controllers.course_controller import course_bp
from app.controllers.mission_controller import mission_bp

__all__ = [
    "auth_bp",
    "admin_bp",
    "user_bp",
    "course_bp",
    "mission_bp",
]
