from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.services import UserService, CourseService, MissionService

user_bp = Blueprint("user", __name__)


@user_bp.route("/dashboard")
@login_required
def dashboard():
    """User dashboard."""
    courses = CourseService.get_all_courses()[:6]  # Get first 6 courses
    missions = MissionService.get_user_missions(current_user.id)
    
    all_users = UserService.get_all_users()
    user_stats = []
    for u in all_users:
        if u.role == "ADMIN":
            continue
        completed_tasks = 0
        completed_missions = 0
        for m in u.missions.all():
            tasks = m.tasks.all()
            if not tasks:
                continue
            is_mission_complete = True
            for t in tasks:
                if t.isCompleted:
                    completed_tasks += 1
                else:
                    is_mission_complete = False
            if is_mission_complete:
                completed_missions += 1
                
        user_stats.append({
            "user": u,
            "completed_missions": completed_missions,
            "completed_tasks": completed_tasks
        })
        
    # Sort by completed_missions descending, then completed_tasks descending
    user_stats.sort(key=lambda x: (x["completed_missions"], x["completed_tasks"]), reverse=True)
    
    return render_template(
        "user/dashboard.html",
        courses=courses,
        missions=missions,
        user_stats=user_stats,
    )


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """User profile page."""
    if request.method == "POST":
        name = request.form.get("name", current_user.name).strip()
        description = request.form.get("description", current_user.description or "").strip() or None
        avatar = request.form.get("avatar", "").strip() or None
        wallpaper = request.form.get("wallpaper", "").strip() or None
        
        UserService.update_user_profile(current_user.id, name, description, avatar, wallpaper)
        flash("Cập nhật hồ sơ thành công.", "success")
        return redirect(url_for("user.profile"))
    
    return render_template("user/profile.html")
