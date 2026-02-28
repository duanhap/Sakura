from app.repositories import UnitRepository, TaskRepository


class UnitService:
    """Service for unit operations"""

    @staticmethod
    def get_unit(unit_id):
        """Get unit by ID."""
        return UnitRepository.get_by_id(unit_id)

    @staticmethod
    def get_units_by_course(course_id):
        """Get all units of a course."""
        return UnitRepository.get_by_course(course_id)

    def get_units_by_course_paginated(course_id, page: int = 1, per_page: int = 20):
        """Return a pagination object for units in a course.

        ``page`` and ``per_page`` parameters support simple paging in the
        admin UI when there are many units.
        """
        query = UnitRepository.query_by_course(course_id)
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def create_unit(name: str, course_id: int, description=None, video=None, document=None) -> dict:
        """Create a new unit."""
        if not name:
            return {"success": False, "message": "Tên bài học không được để trống."}
        
        unit = UnitRepository.create(
            name=name.strip(),
            course_id=course_id,
            description=description.strip() if description else None,
            video=video.strip() if video else None,
            document=document.strip() if document else None,
        )
        return {"success": True, "message": "Tạo bài học thành công.", "unit": unit}

    @staticmethod
    def update_unit(unit_id: int, name: str, description=None, video=None, document=None) -> dict:
        """Update a unit."""
        if not name:
            return {"success": False, "message": "Tên bài học không được để trống."}
        
        unit = UnitRepository.update(
            unit_id,
            name=name.strip(),
            description=description.strip() if description else None,
            video=video.strip() if video else None,
            document=document.strip() if document else None,
        )
        return {"success": True, "message": "Cập nhật bài học thành công.", "unit": unit}

    @staticmethod
    def delete_unit(unit_id: int):
        """Delete a unit and all its tasks."""
        unit = UnitRepository.get_by_id(unit_id)
        if unit:
            course_id = unit.Courseid
            # Delete all tasks of this unit
            tasks = TaskRepository.get_by_unit(unit_id)
            for task in tasks:
                TaskRepository.delete(task.id)
            # Delete unit
            UnitRepository.delete(unit_id)
            return {"success": True, "message": "Đã xóa bài học.", "course_id": course_id}
        return {"success": False, "message": "Bài học không tồn tại."}
