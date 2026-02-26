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
    
    return render_template(
        "user/dashboard.html",
        courses=courses,
        missions=missions,
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
