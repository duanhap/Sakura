from app.extensions import db
from app.models import Course


class CourseRepository:
    """Repository for Course model"""

    @staticmethod
    def get_by_id(course_id):
        """Get course by ID."""
        return Course.query.get(course_id)

    @staticmethod
    def get_all():
        """Get all courses."""
        return Course.query.order_by(Course.createdAt.desc()).all()

    @staticmethod
    def create(name, languageCourse, description, image=None):
        """Create a new course."""
        course = Course(
            name=name,
            languageCourse=languageCourse,
            description=description,
            image=image,
        )
        db.session.add(course)
        db.session.commit()
        return course

    @staticmethod
    def update(course_id, **kwargs):
        """Update course fields."""
        course = Course.query.get(course_id)
        if course:
            for key, value in kwargs.items():
                if hasattr(course, key):
                    setattr(course, key, value)
            db.session.commit()
        return course

    @staticmethod
    def delete(course_id):
        """Delete a course."""
        course = Course.query.get(course_id)
        if course:
            db.session.delete(course)
            db.session.commit()
        return course

    @staticmethod
    def count():
        """Count total courses."""
        return Course.query.count()
