from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.services import UnitService, FlashcardService
from app.utils import is_admin

unit_bp = Blueprint("unit", __name__, url_prefix="/units")

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            flash("Bạn không có quyền truy cập trang này.", "danger")
            return redirect(url_for("course.list"))
        return f(*args, **kwargs)
    return decorated_function

@unit_bp.route("/<int:unit_id>")
@login_required
def detail(unit_id):
    """Unit detail page showing flashcard and practice options."""
    unit = UnitService.get_unit(unit_id)
    if not unit:
        flash("Bài học không tồn tại.", "danger")
        return redirect(url_for("course.list"))
    
    return render_template("units/detail.html", unit=unit)

@unit_bp.route("/<int:unit_id>/flashcards/new", methods=["GET", "POST"])
@login_required
@admin_required
def flashcard_new(unit_id):
    """Add a new flashcard to a unit."""
    unit = UnitService.get_unit(unit_id)
    if not unit:
        flash("Bài học không tồn tại.", "danger")
        return redirect(url_for("course.list"))
        
    if request.method == "POST":
        term = request.form.get("term", "").strip()
        pronunciation = request.form.get("pronunciation", "").strip()
        description = request.form.get("description", "").strip()
        memory_tip = request.form.get("memory_tip", "").strip()
        
        result = FlashcardService.create_flashcard(unit_id, term, pronunciation, description, memory_tip)
        flash(result["message"], "success" if result["success"] else "danger")
        if result["success"]:
            return redirect(url_for("unit.detail", unit_id=unit_id))
            
    return render_template("units/flashcard_form.html", unit=unit, card=None)

@unit_bp.route("/<int:unit_id>/flashcards/<int:flashcard_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def flashcard_edit(unit_id, flashcard_id):
    """Edit a flashcard."""
    unit = UnitService.get_unit(unit_id)
    card = FlashcardService.get_flashcard(flashcard_id)
    
    if not unit or not card or card.UnitId != unit_id:
        flash("Dữ liệu không hợp lệ.", "danger")
        return redirect(url_for("unit.detail", unit_id=unit_id))
        
    if request.method == "POST":
        term = request.form.get("term", "").strip()
        pronunciation = request.form.get("pronunciation", "").strip()
        description = request.form.get("description", "").strip()
        memory_tip = request.form.get("memory_tip", "").strip()
        
        result = FlashcardService.update_flashcard(flashcard_id, term, pronunciation, description, memory_tip)
        flash(result["message"], "success" if result["success"] else "danger")
        if result["success"]:
            return redirect(url_for("unit.detail", unit_id=unit_id))
            
    return render_template("units/flashcard_form.html", unit=unit, card=card)

@unit_bp.route("/<int:unit_id>/flashcards/<int:flashcard_id>/delete", methods=["POST"])
@login_required
@admin_required
def flashcard_delete(unit_id, flashcard_id):
    """Delete a flashcard."""
    result = FlashcardService.delete_flashcard(flashcard_id)
    flash(result["message"], "info" if result["success"] else "danger")
    return redirect(url_for("unit.detail", unit_id=unit_id))

@unit_bp.route("/<int:unit_id>/flashcards/import", methods=["GET", "POST"])
@login_required
@admin_required
def flashcard_import(unit_id):
    """Import flashcards from a file."""
    unit = UnitService.get_unit(unit_id)
    if not unit:
        flash("Bài học không tồn tại.", "danger")
        return redirect(url_for("course.list"))
        
    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename != '':
            try:
                # Read text ignoring decode errors, mostly utf-8
                text_content = file.read().decode('utf-8', errors='ignore')
                result = FlashcardService.process_document(unit_id, text_content)
                flash(result["message"], "success" if result["success"] else "danger")
                if result["success"]:
                    return redirect(url_for("unit.detail", unit_id=unit_id))
            except Exception as e:
                flash("Có lỗi xảy ra khi đọc file.", "danger")
        else:
            flash("Vui lòng chọn một file hợp lệ.", "danger")
            
    return render_template("units/flashcard_import.html", unit=unit)

@unit_bp.route("/<int:unit_id>/flashcards/study")
@login_required
def flashcards_study(unit_id):
    """Study mode for flashcards."""
    unit = UnitService.get_unit(unit_id)
    if not unit:
        flash("Bài học không tồn tại.", "danger")
        return redirect(url_for("course.list"))
        
    flashcards = FlashcardService.get_flashcards_with_status(unit_id, current_user.id)
    return render_template("units/flashcards_study.html", unit=unit, flashcards=flashcards)

@unit_bp.route("/<int:unit_id>/flashcards/<int:flashcard_id>/status", methods=["POST"])
@login_required
def update_flashcard_status(unit_id, flashcard_id):
    """API to update user status for a flashcard."""
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({"success": False, "message": "Invalid request"}), 400
        
    status = data['status']
    result = FlashcardService.update_user_status(flashcard_id, current_user.id, status)
    
    if result["success"]:
        return jsonify(result), 200
    return jsonify(result), 400
