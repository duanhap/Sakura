from werkzeug.security import generate_password_hash, check_password_hash
from app.repositories import UserRepository


class AuthService:
    """Service for authentication operations"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password."""
        return generate_password_hash(password)

    @staticmethod
    def verify_password(hashed_password: str, password: str) -> bool:
        """Verify a password against its hash."""
        return check_password_hash(hashed_password, password)

    @staticmethod
    def login(email: str, password: str):
        """Authenticate user by email and password."""
        email = email.strip().lower()
        user = UserRepository.get_by_email(email)
        if user and AuthService.verify_password(user.password, password):
            return user
        return None

    @staticmethod
    def is_email_exists(email: str) -> bool:
        """Check if email already exists."""
        return UserRepository.get_by_email(email.strip().lower()) is not None

    @staticmethod
    def register_user(name: str, email: str, password: str, role: str = "USER") -> dict:
        """Register a new user."""
        email = email.strip().lower()
        
        if not name or not email or not password:
            return {"success": False, "message": "Tên, email và mật khẩu không được để trống."}
        
        if AuthService.is_email_exists(email):
            return {"success": False, "message": "Email đã tồn tại trong hệ thống."}
        
        hashed_password = AuthService.hash_password(password)
        user = UserRepository.create(
            name=name,
            email=email,
            password_hash=hashed_password,
            role=role,
        )
        return {"success": True, "message": "Tạo tài khoản thành công.", "user": user}
