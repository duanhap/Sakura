from app.extensions import db
from app.models import Task


class TaskRepository:
    """Repository for Task model"""

    @staticmethod
    def get_by_id(task_id):
        """Get task by ID."""
        return Task.query.get(task_id)

    @staticmethod
    def get_by_mission(mission_id):
        """Get tasks by mission ID."""
        return Task.query.filter_by(Missionid=mission_id).order_by(Task.id.asc()).all()

    @staticmethod
    def get_by_unit(unit_id):
        """Get tasks by unit ID."""
        return Task.query.filter_by(Unitid=unit_id).order_by(Task.id.asc()).all()

    @staticmethod
    def get_all():
        """Get all tasks."""
        return Task.query.order_by(Task.id.asc()).all()

    @staticmethod
    def create(name, mission_id, unit_id, is_completed=False):
        """Create a new task."""
        task = Task(
            name=name,
            Missionid=mission_id,
            Unitid=unit_id,
            isCompleted=is_completed,
        )
        db.session.add(task)
        db.session.commit()
        return task

    @staticmethod
    def update(task_id, **kwargs):
        """Update task fields."""
        task = Task.query.get(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            db.session.commit()
        return task

    @staticmethod
    def delete(task_id):
        """Delete a task."""
        task = Task.query.get(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
        return task

    @staticmethod
    def count():
        """Count total tasks."""
        return Task.query.count()
