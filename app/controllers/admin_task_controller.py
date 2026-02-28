from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app.services import MissionService
from app.repositories import TaskRepository, UnitRepository


admin_task_bp = Blueprint("admin_task", __name__, url_prefix="/admin/tasks")


def is_admin_required(f):
    """Decorator to check if user is admin."""
    from functools import wraps
    from app.utils import is_admin
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            flash("Bạn không có quyền truy cập trang này.", "danger")
            return redirect(url_for("user.dashboard"))
        return f(*args, **kwargs)
    return decorated_function


@admin_task_bp.route("/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
@is_admin_required
def edit(task_id):
    """Edit task."""
    task = TaskRepository.get_by_id(task_id)
    if not task:
        flash("Task không tồn tại.", "danger")
        return redirect(url_for("admin.missions"))
    
    units = UnitRepository.get_all()
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        unit_id = request.form.get("unit_id", "").strip()
        
        is_completed = request.form.get("is_completed") == "on"
        if not name:
            flash("Tên task không được để trống.", "danger")
        else:
            # Only pass unit_id if it's not empty
            task_data = {"name": name, "is_completed": is_completed}
            if unit_id:
                task_data["unit_id"] = unit_id
            result = MissionService.update_task(task_id, **task_data)
            if result["success"]:
                flash(result["message"], "success")
                return redirect(url_for("admin_mission.detail", mission_id=task.Missionid))
            else:
                flash(result["message"], "danger")
    
    return render_template("admin/task_form.html", task=task, units=units)


@admin_task_bp.route("/<int:task_id>/delete", methods=["POST"])
@login_required
@is_admin_required
def delete(task_id):
    """Delete task."""
    task = TaskRepository.get_by_id(task_id)
    if not task:
        flash("Task không tồn tại.", "danger")
        return redirect(url_for("admin.missions"))
    
    mission_id = task.Missionid
    result = MissionService.delete_task(task_id)
    flash(result.get("message", ""), "info" if result.get("success") else "danger")
    return redirect(url_for("admin_mission.detail", mission_id=mission_id))
