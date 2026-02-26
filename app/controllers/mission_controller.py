from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services import MissionService
from app.utils import is_admin
from app.models import Task

mission_bp = Blueprint("mission", __name__, url_prefix="/missions")


@mission_bp.route("/")
@login_required
def list():
    """List user missions."""
    missions = MissionService.get_user_missions(current_user.id)
    return render_template("missions/list.html", missions=missions)


@mission_bp.route("/<int:mission_id>")
@login_required
def detail(mission_id):
    """Mission detail page."""
    mission = MissionService.get_mission(mission_id)
    if not mission:
        flash("Mission không tồn tại.", "danger")
        return redirect(url_for("mission.list"))
    
    if mission.Userid != current_user.id and not is_admin():
        flash("Bạn không có quyền xem mission này.", "danger")
        return redirect(url_for("mission.list"))
    
    # order tasks by their primary key (id) ascending
    tasks = mission.tasks.order_by(Task.id.asc()).all()
    progress_data = MissionService.get_mission_progress(mission_id)
    
    return render_template(
        "missions/detail.html",
        mission=mission,
        tasks=tasks,
        progress=progress_data["progress"],
    )


@mission_bp.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id):
    """Toggle task completion status."""
    result = MissionService.toggle_task(task_id, current_user.id, is_admin())
    
    if result["success"]:
        flash(result["message"], "success")
    else:
        flash(result["message"], "danger")
    
    # Return to mission detail page
    from app.repositories import TaskRepository
    task = TaskRepository.get_by_id(task_id)
    return redirect(url_for("mission.detail", mission_id=task.Missionid))
