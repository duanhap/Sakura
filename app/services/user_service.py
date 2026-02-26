from app.repositories import UserRepository


class UserService:
    """Service for user operations"""

    @staticmethod
    def get_user(user_id):
        """Get user by ID."""
        return UserRepository.get_by_id(user_id)

    @staticmethod
    def get_all_users():
        """Get all users."""
        return UserRepository.get_all()

    @staticmethod
    def update_user_profile(user_id, name=None, description=None, avatar=None, wallpaper=None):
        """Update user profile."""
        update_data = {}
        if name:
            update_data["name"] = name.strip()
        if description is not None:
            update_data["description"] = description.strip() or None
        if avatar is not None:
            update_data["avatar"] = avatar.strip() or None
        if wallpaper is not None:
            update_data["wallpaper"] = wallpaper.strip() or None
        
        return UserRepository.update(user_id, **update_data)

    @staticmethod
    def get_total_users():
        """Get total number of users."""
        return UserRepository.count()
