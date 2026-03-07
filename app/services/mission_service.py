from app.repositories import MissionRepository, TaskRepository
from app.services.test_service import TestService


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
    def create_mission(name: str, user_id, unit_ids: list, description=None) -> dict:
        """Create a new mission with tasks for one or more users.

        ``user_id`` may be an integer, list of integers, or the string "ALL" to
        assign to every user in the system.  When multiple users are passed a
        separate mission row will be created for each.  The return value will
        include either a single mission object or a list of missions.
        """
        if not name or not user_id:
            return {"success": False, "message": "Tên mission và người dùng không được để trống."}
        
        missions_created = []
        user_ids = []
        # resolve user_id variants
        if user_id == "ALL":
            from app.models import User
            user_ids = [u.id for u in User.query.all()]
        elif isinstance(user_id, list):
            user_ids = [int(u) for u in user_id if u]
        else:
            user_ids = [int(user_id)]

        from app.models import User
        for uid in user_ids:
            mission = MissionRepository.create(
                name=name.strip(),
                user_id=uid,
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
            missions_created.append(mission)

        result = {"success": True, "message": "Tạo mission thành công.", "mission": missions_created[0] if len(missions_created) == 1 else missions_created}
        return result

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
        
        # Nếu task được đánh dấu là chưa hoàn thành -> muốn chuyển sang hoàn thành
        if not task.isCompleted:
            # Kiểm tra nếu task có gắn với Unit
            if task.Unitid:
                record = TestService.get_record(current_user_id, task.Unitid)
                # Nếu chưa có kỷ lục hoặc kỷ lục dưới 85%
                if not record or record.get('score', 0) < 85:
                    return {
                        "success": False, 
                        "message": f"🌸 Hù! Bạn chưa đạt kỉ lục 85% cho bài học này đâu nè. Hãy cố gắng ôn tập thêm một chút để hoàn thành task nhé! ✨ (Kỉ lục hiện tại: {record['score'] if record else 0}%)"
                    }

        task = TaskRepository.update(task_id, isCompleted=not task.isCompleted)
        return {"success": True, "message": "Tuyệt vời! Cập nhật trạng thái task thành công. ✨", "task": task}

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

    @staticmethod
    def update_mission(mission_id: int, name: str = None, description: str = None, user_id: int = None) -> dict:
        """Update mission fields."""
        mission = MissionRepository.get_by_id(mission_id)
        if not mission:
            return {"success": False, "message": "Mission không tồn tại."}
        data = {}
        if name is not None:
            data['name'] = name.strip()
        if description is not None:
            data['description'] = description.strip()
        if user_id is not None:
            data['Userid'] = int(user_id)
        mission = MissionRepository.update(mission_id, **data)
        return {"success": True, "message": "Cập nhật mission thành công.", "mission": mission}

    @staticmethod
    def add_task(mission_id: int, name: str, unit_id: int = None, is_completed: bool = False) -> dict:
        """Create a new task under a mission."""
        if not name or not mission_id:
            return {"success": False, "message": "Tên task và mission không được để trống."}
        task = TaskRepository.create(
            name=name.strip(),
            mission_id=mission_id,
            unit_id=int(unit_id) if unit_id else None,
            is_completed=bool(is_completed),
        )
        return {"success": True, "message": "Tạo task thành công.", "task": task}

    @staticmethod
    def update_task(task_id: int, **kwargs) -> dict:
        """Update task fields like name, unit_id, isCompleted."""
        task = TaskRepository.get_by_id(task_id)
        if not task:
            return {"success": False, "message": "Task không tồn tại."}
        data = {}
        if 'name' in kwargs and kwargs['name'] is not None:
            data['name'] = kwargs['name'].strip()
        if 'unit_id' in kwargs:
            # if client sent empty string, clear association
            if kwargs['unit_id'] == '' or kwargs['unit_id'] is None:
                data['Unitid'] = None
            else:
                data['Unitid'] = int(kwargs['unit_id'])
        if 'is_completed' in kwargs and kwargs['is_completed'] is not None:
            data['isCompleted'] = bool(kwargs['is_completed'])
        task = TaskRepository.update(task_id, **data)
        return {"success": True, "message": "Cập nhật task thành công.", "task": task}

    @staticmethod
    def delete_task(task_id: int) -> dict:
        """Delete a task."""
        task = TaskRepository.get_by_id(task_id)
        if task:
            TaskRepository.delete(task_id)
            return {"success": True, "message": "Đã xóa task."}
        return {"success": False, "message": "Task không tồn tại."}
