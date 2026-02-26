from flask import Blueprint, render_template
from flask_login import login_required
from app.services import CourseService
from app.models import Unit

course_bp = Blueprint("course", __name__, url_prefix="/courses")


@course_bp.route("/")
@login_required
def list():
    """List all courses."""
    courses = CourseService.get_all_courses()
    return render_template("courses/list.html", courses=courses)


@course_bp.route("/<int:course_id>")
@login_required
def detail(course_id):
    """Course detail page."""
    course = CourseService.get_course(course_id)
    if not course:
        from flask import flash, redirect, url_for
        flash("Khóa học không tồn tại.", "danger")
        return redirect(url_for("course.list"))
    
    # order units by creation date (ascending)
    units = course.units.order_by(Unit.createdAt.asc()).all()
    return render_template("courses/detail.html", course=course, units=units)
