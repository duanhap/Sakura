from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.utils import is_admin
from app.services import AuthService, UserService, CourseService, MissionService
from app.repositories import UnitRepository

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    """Decorator to check if user is admin."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            flash("Bạn không có quyền truy cập trang này.", "danger")
            return redirect(url_for("user.dashboard"))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    """Admin dashboard."""
    from app.repositories import UserRepository, CourseRepository, MissionRepository, TaskRepository
    user_count = UserRepository.count()
    course_count = CourseRepository.count()
    mission_count = MissionRepository.count()
    task_count = TaskRepository.count()
    users = UserRepository.get_all()
    
    return render_template(
        "admin/dashboard.html",
        user_count=user_count,
        course_count=course_count,
        mission_count=mission_count,
        task_count=task_count,
        users=users,
    )


@admin_bp.route("/courses", methods=["GET"])
@login_required
@admin_required
def courses():
    """List all courses."""
    courses = CourseService.get_all_courses()
    return render_template("admin/courses.html", courses=courses)


@admin_bp.route("/courses/new", methods=["GET", "POST"])
@login_required
@admin_required
def course_new():
    """Create new course."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        image = request.form.get("image", "").strip() or None
        
        result = CourseService.create_course(name, description, image)
        if result["success"]:
            flash(result["message"], "success")
            return redirect(url_for("admin.courses"))
        else:
            flash(result["message"], "danger")
    
    return render_template("admin/course_form.html", course=None)


@admin_bp.route("/courses/<int:course_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def course_edit(course_id):
    """Edit a course."""
    course = CourseService.get_course(course_id)
    if not course:
        flash("Khóa học không tồn tại.", "danger")
        return redirect(url_for("admin.courses"))
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        image = request.form.get("image", "").strip() or None
        
        result = CourseService.update_course(course_id, name, description, image)
        if result["success"]:
            flash(result["message"], "success")
            return redirect(url_for("admin.courses"))
        else:
            flash(result["message"], "danger")
    
    return render_template("admin/course_form.html", course=course)


@admin_bp.route("/courses/<int:course_id>/delete", methods=["POST"])
@login_required
@admin_required
def course_delete(course_id):
    """Delete a course."""
    result = CourseService.delete_course(course_id)
    flash(result["message"], "info" if result["success"] else "danger")
    return redirect(url_for("admin.courses"))


@admin_bp.route("/courses/<int:course_id>/units/new", methods=["GET", "POST"])
@login_required
@admin_required
def unit_new(course_id):
    """Create new unit."""
    from app.services import UnitService
    course = CourseService.get_course(course_id)
    if not course:
        flash("Khóa học không tồn tại.", "danger")
        return redirect(url_for("admin.courses"))
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip() or None
        video = request.form.get("video", "").strip() or None
        document = request.form.get("document", "").strip() or None
        
        result = UnitService.create_unit(name, course_id, description, video, document)
        if result["success"]:
            flash(result["message"], "success")
            return redirect(url_for("admin.units", course_id=course_id))
        else:
            flash(result["message"], "danger")
    
    return render_template("admin/unit_form.html", course=course)


@admin_bp.route("/courses/<int:course_id>/units")
@login_required
@admin_required
def units(course_id):
    """List units of a course."""
    from app.services import UnitService
    course = CourseService.get_course(course_id)
    if not course:
        flash("Khóa học không tồn tại.", "danger")
        return redirect(url_for("admin.courses"))
    
    units = UnitService.get_units_by_course(course_id)
    return render_template("admin/units.html", course=course, units=units)


@admin_bp.route("/units/<int:unit_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def unit_edit(unit_id):
    """Edit a unit."""
    from app.services import UnitService
    unit = UnitService.get_unit(unit_id)
    if not unit:
        flash("Bài học không tồn tại.", "danger")
        return redirect(url_for("admin.courses"))
    
    course = unit.course
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip() or None
        video = request.form.get("video", "").strip() or None
        document = request.form.get("document", "").strip() or None
        
        result = UnitService.update_unit(unit_id, name, description, video, document)
        if result["success"]:
            flash(result["message"], "success")
            return redirect(url_for("admin.units", course_id=course.id))
        else:
            flash(result["message"], "danger")
    
    return render_template("admin/unit_form.html", course=course, unit=unit)


@admin_bp.route("/units/<int:unit_id>/delete", methods=["POST"])
@login_required
@admin_required
def unit_delete(unit_id):
    """Delete a unit."""
    from app.services import UnitService
    result = UnitService.delete_unit(unit_id)
    flash(result["message"], "info" if result["success"] else "danger")
    course_id = result.get("course_id")
    if course_id:
        return redirect(url_for("admin.units", course_id=course_id))
    return redirect(url_for("admin.courses"))


@admin_bp.route("/missions")
@login_required
@admin_required
def missions():
    """List all missions."""
    missions = MissionService.get_all_missions()
    return render_template("admin/missions.html", missions=missions)


@admin_bp.route("/missions/new", methods=["GET", "POST"])
@login_required
@admin_required
def mission_new():
    """Create new mission."""
    from app.repositories import UserRepository
    users = UserRepository.get_all()
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip() or None
        user_id = request.form.get("user_id")
        
        result = MissionService.create_mission(name, int(user_id) if user_id else None, [], description)
        if result["success"]:
            flash(result["message"], "success")
            return redirect(url_for("admin.missions"))
        else:
            flash(result["message"], "danger")
    
    return render_template("admin/mission_form.html", users=users)


@admin_bp.route("/users/new", methods=["GET", "POST"])
@login_required
@admin_required
def user_new():
    """Create new user."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "USER").strip().upper() or "USER"
        avatar = request.form.get("avatar", "").strip() or None
        wallpaper = request.form.get("wallpaper", "").strip() or None
        
        result = AuthService.register_user(name, email, password, role)
        if result["success"]:
            # Update additional fields
            from app.repositories import UserRepository
            user = result["user"]
            UserRepository.update(user.id, avatar=avatar, wallpaper=wallpaper)
            flash(result["message"], "success")
            return redirect(url_for("admin.dashboard"))
        else:
            flash(result["message"], "danger")
    
    return render_template("admin/user_form.html")
