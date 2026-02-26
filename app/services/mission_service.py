from app.repositories import MissionRepository, TaskRepository


class MissionService:
    """Service for mission operations"""

    @staticmethod
    def get_mission(mission_id):
        """Get mission by ID."""
        return MissionRepository.get_by_id(mission_id)

    @staticmethod
    def get_user_missions(user_id):
        """Get all missions of a user."""
        return MissionRepository.get_by_user(user_id)

    @staticmethod
    def get_all_missions():
        """Get all missions."""
        return MissionRepository.get_all()

    @staticmethod
    def create_mission(name: str, user_id: int, unit_ids: list, description=None) -> dict:
        """Create a new mission with tasks."""
        if not name or not user_id:
            return {"success": False, "message": "Tên mission và người dùng không được để trống."}
        
        mission = MissionRepository.create(
            name=name.strip(),
            user_id=user_id,
            description=description.strip() if description else None,
        )
        
        # Create tasks for each unit
        for unit_id in unit_ids:
            if unit_id:
                TaskRepository.create(
                    name=f"Hoàn thành bài học #{unit_id}",
                    mission_id=mission.id,
                    unit_id=int(unit_id),
                    is_completed=False,
                )
        
        return {"success": True, "message": "Tạo mission thành công.", "mission": mission}

    @staticmethod
    def delete_mission(mission_id: int):
        """Delete a mission and all its tasks."""
        mission = MissionRepository.get_by_id(mission_id)
        if mission:
            # Delete all tasks
            tasks = TaskRepository.get_by_mission(mission_id)
            for task in tasks:
                TaskRepository.delete(task.id)
            # Delete mission
            MissionRepository.delete(mission_id)
            return {"success": True, "message": "Đã xóa mission."}
        return {"success": False, "message": "Mission không tồn tại."}

    @staticmethod
    def toggle_task(task_id: int, current_user_id: int, is_admin: bool) -> dict:
        """Toggle task completion status."""
        task = TaskRepository.get_by_id(task_id)
        if not task:
            return {"success": False, "message": "Task không tồn tại."}
        
        if task.mission.Userid != current_user_id and not is_admin:
            return {"success": False, "message": "Bạn không có quyền cập nhật task này."}
        
        task = TaskRepository.update(task_id, isCompleted=not task.isCompleted)
        return {"success": True, "message": "Cập nhật trạng thái task thành công.", "task": task}

    @staticmethod
    def get_mission_progress(mission_id):
        """Get mission progress."""
        tasks = TaskRepository.get_by_mission(mission_id)
        total = len(tasks)
        completed = len([t for t in tasks if t.isCompleted])
        progress = int((completed / total) * 100) if total else 0
        return {
            "total": total,
            "completed": completed,
            "progress": progress,
        }

    @staticmethod
    def get_total_missions():
        """Get total number of missions."""
        return MissionRepository.count()
