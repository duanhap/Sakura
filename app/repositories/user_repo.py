from app.extensions import db
from app.models import User


class UserRepository:
    """Repository for User model"""

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID."""
        return User.query.get(user_id)

    @staticmethod
    def get_by_email(email):
        """Get user by email."""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_all():
        """Get all users."""
        return User.query.order_by(User.createdAt.desc()).all()

    @staticmethod
    def create(name, email, password_hash, role="USER", avatar=None, wallpaper=None, description=None):
        """Create a new user."""
        user = User(
            name=name,
            email=email,
            password=password_hash,
            role=role,
            avatar=avatar,
            wallpaper=wallpaper,
            description=description,
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update(user_id, **kwargs):
        """Update user fields."""
        user = User.query.get(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            db.session.commit()
        return user

    @staticmethod
    def delete(user_id):
        """Delete a user."""
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
        return user

    @staticmethod
    def count():
        """Count total users."""
        return User.query.count()
