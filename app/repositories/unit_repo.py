from app.extensions import db
from app.models import Unit


class UnitRepository:
    """Repository for Unit model"""

    @staticmethod
    def get_by_id(unit_id):
        """Get unit by ID."""
        return Unit.query.get(unit_id)

    @staticmethod
    def get_by_course(course_id):
        """Get units by course ID."""
        return Unit.query.filter_by(Courseid=course_id).order_by(Unit.createdAt.asc()).all()

    @staticmethod
    def get_all():
        """Get all units."""
        return Unit.query.order_by(Unit.createdAt.desc()).all()

    @staticmethod
    def create(name, course_id, description=None, video=None, document=None):
        """Create a new unit."""
        unit = Unit(
            name=name,
            Courseid=course_id,
            description=description,
            video=video,
            document=document,
        )
        db.session.add(unit)
        db.session.commit()
        return unit

    @staticmethod
    def update(unit_id, **kwargs):
        """Update unit fields."""
        unit = Unit.query.get(unit_id)
        if unit:
            for key, value in kwargs.items():
                if hasattr(unit, key):
                    setattr(unit, key, value)
            db.session.commit()
        return unit

    @staticmethod
    def delete(unit_id):
        """Delete a unit."""
        unit = Unit.query.get(unit_id)
        if unit:
            db.session.delete(unit)
            db.session.commit()
        return unit
