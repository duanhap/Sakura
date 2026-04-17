from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services import CourseService, FlashcardService
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
        flash("Khóa học không tồn tại.", "danger")
        return redirect(url_for("course.list"))
    
    # order units by creation date (ascending)
    units = course.units.order_by(Unit.createdAt.asc()).all()
    return render_template("courses/detail.html", course=course, units=units)


@course_bp.route("/<int:course_id>/flashcards")
@login_required
def flashcards(course_id):
    """Course-wide flashcards summary."""
    course = CourseService.get_course(course_id)
    if not course:
        flash("Khóa học không tồn tại.", "danger")
        return redirect(url_for("course.list"))
    
    flashcards = FlashcardService.get_flashcards_by_course(course_id, current_user.id)
    return render_template("courses/flashcards.html", course=course, flashcards=flashcards)


@course_bp.route("/<int:course_id>/matching-game")
@login_required
def matching_game(course_id):
    """Course-wide matching game."""
    course = CourseService.get_course(course_id)
    if not course:
        flash("Khóa học không tồn tại.", "danger")
        return redirect(url_for("course.list"))
    
    flashcards = FlashcardService.get_flashcards_by_course(course_id)
    return render_template("courses/matching_game.html", course=course, flashcards=flashcards)
