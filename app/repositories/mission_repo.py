from app.extensions import db
from app.models import Mission


class MissionRepository:
    """Repository for Mission model"""

    @staticmethod
    def get_by_id(mission_id):
        """Get mission by ID."""
        return Mission.query.get(mission_id)

    @staticmethod
    def get_by_user(user_id):
        """Get missions by user ID."""
        return Mission.query.filter_by(Userid=user_id).order_by(Mission.createdAt.desc()).all()

    @staticmethod
    def get_all():
        """Get all missions."""
        return Mission.query.order_by(Mission.createdAt.desc()).all()

    @staticmethod
    def create(name, user_id, description=None):
        """Create a new mission."""
        mission = Mission(
            name=name,
            Userid=user_id,
            description=description,
        )
        db.session.add(mission)
        db.session.commit()
        return mission

    @staticmethod
    def update(mission_id, **kwargs):
        """Update mission fields."""
        mission = Mission.query.get(mission_id)
        if mission:
            for key, value in kwargs.items():
                if hasattr(mission, key):
                    setattr(mission, key, value)
            db.session.commit()
        return mission

    @staticmethod
    def delete(mission_id):
        """Delete a mission."""
        mission = Mission.query.get(mission_id)
        if mission:
            db.session.delete(mission)
            db.session.commit()
        return mission

    @staticmethod
    def count():
        """Count total missions."""
        return Mission.query.count()
