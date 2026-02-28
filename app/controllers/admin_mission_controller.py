from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app.services import MissionService, CourseService
from app.repositories import UserRepository, UnitRepository, TaskRepository
from app.models import Task

admin_mission_bp = Blueprint("admin_mission", __name__, url_prefix="/admin/missions")


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


@admin_mission_bp.route("/<int:mission_id>")
@login_required
@is_admin_required
def detail(mission_id):
    """View mission details with tasks."""
    mission = MissionService.get_mission(mission_id)
    if not mission:
        flash("Mission không tồn tại.", "danger")
        return redirect(url_for("admin.missions"))
    
    tasks = Task.query.filter_by(Missionid=mission_id).order_by(Task.id.asc()).all()
    units = UnitRepository.get_all()
    return render_template("admin/mission_detail.html", mission=mission, tasks=tasks, units=units)


@admin_mission_bp.route("/<int:mission_id>/edit", methods=["GET", "POST"])
@login_required
@is_admin_required
def edit(mission_id):
    """Edit mission."""
    mission = MissionService.get_mission(mission_id)
    if not mission:
        flash("Mission không tồn tại.", "danger")
        return redirect(url_for("admin.missions"))
    
    users = UserRepository.get_all()
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip() or None
        user_id = request.form.get("user_id")
        
        if not name or not user_id:
            flash("Tên mission và người dùng không được để trống.", "danger")
        else:
            result = MissionService.update_mission(mission_id, name, description, int(user_id))
            if result["success"]:
                flash(result["message"], "success")
                return redirect(url_for("admin_mission.detail", mission_id=mission_id))
            else:
                flash(result["message"], "danger")
    
    return render_template("admin/mission_form.html", mission=mission, users=users)


@admin_mission_bp.route("/<int:mission_id>/delete", methods=["POST"])
@login_required
@is_admin_required
def delete(mission_id):
    """Delete mission."""
    result = MissionService.delete_mission(mission_id)
    flash(result.get("message", ""), "info" if result.get("success") else "danger")
    return redirect(url_for("admin.missions"))


@admin_mission_bp.route("/<int:mission_id>/tasks/new", methods=["POST"])
@login_required
@is_admin_required
def task_new(mission_id):
    """Create new task under a mission."""
    mission = MissionService.get_mission(mission_id)
    if not mission:
        flash("Mission không tồn tại.", "danger")
        return redirect(url_for("admin.missions"))
    
    name = request.form.get("name", "").strip()
    unit_id = request.form.get("unit_id")
    is_completed = request.form.get("is_completed") == "on"
    
    if not name:
        flash("Tên task không được để trống.", "danger")
    else:
        result = MissionService.add_task(mission_id, name, unit_id, is_completed)
        flash(result.get("message", ""), "success" if result.get("success") else "danger")
    
    return redirect(url_for("admin_mission.detail", mission_id=mission_id))
