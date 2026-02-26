from app.repositories import CourseRepository, UnitRepository, TaskRepository


class CourseService:
    """Service for course operations"""

    @staticmethod
    def get_course(course_id):
        """Get course by ID."""
        return CourseRepository.get_by_id(course_id)

    @staticmethod
    def get_all_courses():
        """Get all courses."""
        return CourseRepository.get_all()

    @staticmethod
    def create_course(name: str, description: str, image=None) -> dict:
        """Create a new course."""
        if not name or not description:
            return {"success": False, "message": "Tên và mô tả khóa học không được để trống."}
        
        course = CourseRepository.create(
            name=name.strip(),
            description=description.strip(),
            image=image.strip() if image else None,
        )
        return {"success": True, "message": "Tạo khóa học thành công.", "course": course}

    @staticmethod
    def update_course(course_id: int, name: str, description: str, image=None) -> dict:
        """Update a course."""
        if not name or not description:
            return {"success": False, "message": "Tên và mô tả khóa học không được để trống."}
        
        course = CourseRepository.update(
            course_id,
            name=name.strip(),
            description=description.strip(),
            image=image.strip() if image else None,
        )
        return {"success": True, "message": "Cập nhật khóa học thành công.", "course": course}

    @staticmethod
    def delete_course(course_id: int):
        """Delete a course and all its units and tasks."""
        course = CourseRepository.get_by_id(course_id)
        if course:
            # Delete all tasks in units of this course
            units = course.units.all()
            for unit in units:
                TaskRepository.delete(unit.id)
            # Delete all units
            for unit in units:
                UnitRepository.delete(unit.id)
            # Delete course
            CourseRepository.delete(course_id)
            return {"success": True, "message": "Đã xóa khóa học."}
        return {"success": False, "message": "Khóa học không tồn tại."}

    @staticmethod
    def get_total_courses():
        """Get total number of courses."""
        return CourseRepository.count()
