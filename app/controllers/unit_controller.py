from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, Response
from flask_login import login_required, current_user
import requests
import urllib.parse
from app.services import UnitService, FlashcardService, SentenceService, TestService
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

@unit_bp.route("/<int:unit_id>/flashcards/delete_all", methods=["POST"])
@login_required
@admin_required
def flashcard_delete_all(unit_id):
    """Delete all flashcards in a unit."""
    result = FlashcardService.delete_all_flashcards(unit_id)
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

@unit_bp.route("/<int:unit_id>/sentences/new", methods=["GET", "POST"])
@login_required
@admin_required
def sentence_new(unit_id):
    """Add a new sentence to a unit."""
    unit = UnitService.get_unit(unit_id)
    if not unit:
        flash("Bài học không tồn tại.", "danger")
        return redirect(url_for("course.list"))
        
    if request.method == "POST":
        content = request.form.get("content", "").strip()
        pronunciation = request.form.get("pronunciation", "").strip()
        meaning = request.form.get("meaning", "").strip()
        
        result = SentenceService.create_sentence(unit_id, content, pronunciation, meaning)
        flash(result["message"], "success" if result["success"] else "danger")
        if result["success"]:
            return redirect(url_for("unit.detail", unit_id=unit_id))
            
    return render_template("units/sentence_form.html", unit=unit, sentence=None)

@unit_bp.route("/<int:unit_id>/sentences/<int:sentence_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def sentence_edit(unit_id, sentence_id):
    """Edit a sentence."""
    unit = UnitService.get_unit(unit_id)
    sentence = SentenceService.get_sentence(sentence_id)
    
    if not unit or not sentence or sentence.UnitId != unit_id:
        flash("Dữ liệu không hợp lệ.", "danger")
        return redirect(url_for("unit.detail", unit_id=unit_id))
        
    if request.method == "POST":
        content = request.form.get("content", "").strip()
        pronunciation = request.form.get("pronunciation", "").strip()
        meaning = request.form.get("meaning", "").strip()
        
        result = SentenceService.update_sentence(sentence_id, content, pronunciation, meaning)
        flash(result["message"], "success" if result["success"] else "danger")
        if result["success"]:
            return redirect(url_for("unit.detail", unit_id=unit_id))
            
    return render_template("units/sentence_form.html", unit=unit, sentence=sentence)

@unit_bp.route("/<int:unit_id>/sentences/<int:sentence_id>/delete", methods=["POST"])
@login_required
@admin_required
def sentence_delete(unit_id, sentence_id):
    """Delete a sentence."""
    result = SentenceService.delete_sentence(sentence_id)
    flash(result["message"], "info" if result["success"] else "danger")
    return redirect(url_for("unit.detail", unit_id=unit_id))

@unit_bp.route("/<int:unit_id>/sentences/delete_all", methods=["POST"])
@login_required
@admin_required
def sentence_delete_all(unit_id):
    """Delete all sentences in a unit."""
    result = SentenceService.delete_all_sentences(unit_id)
    flash(result["message"], "info" if result["success"] else "danger")
    return redirect(url_for("unit.detail", unit_id=unit_id))

@unit_bp.route("/<int:unit_id>/sentences/import", methods=["GET", "POST"])
@login_required
@admin_required
def sentence_import(unit_id):
    """Import sentences from a file."""
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
                result = SentenceService.process_document(unit_id, text_content)
                flash(result["message"], "success" if result["success"] else "danger")
                if result["success"]:
                    return redirect(url_for("unit.detail", unit_id=unit_id))
            except Exception as e:
                flash("Có lỗi xảy ra khi đọc file.", "danger")
        else:
            flash("Vui lòng chọn một file hợp lệ.", "danger")
            
    return render_template("units/sentence_import.html", unit=unit)


@unit_bp.route("/<int:unit_id>/flashcards/export")
@login_required
@admin_required
def flashcard_export(unit_id):
    """Xuất toàn bộ flashcard của unit ra file .txt theo đúng định dạng import."""
    unit = UnitService.get_unit(unit_id)
    if not unit:
        flash("Bài học không tồn tại.", "danger")
        return redirect(url_for("course.list"))

    flashcards = FlashcardService.get_flashcards_by_unit(unit_id)

    lines = []
    for i, card in enumerate(flashcards, start=1):
        lines.append(f"{i}. Thuật ngữ: {card.term}")
        if card.pronunciation:
            lines.append(f"Cách đọc: {card.pronunciation}")
        if card.description:
            # Tách Mô tả và Ví dụ nếu có
            desc_parts = card.description.split("\nVí dụ: ", 1)
            lines.append(f"Mô tả: {desc_parts[0]}")
            if len(desc_parts) > 1:
                lines.append(f"Ví dụ: {desc_parts[1]}")
        if card.memoryTip:
            lines.append(f"Cách nhớ: {card.memoryTip}")
        lines.append("")  # dòng trống giữa các mục

    content = "\n".join(lines)
    safe_name = unit.name.replace(" ", "_") if unit.name else f"unit_{unit_id}"
    filename = f"flashcards_{safe_name}.txt"
    encoded_filename = urllib.parse.quote(filename)

    return Response(
        content,
        mimetype="text/plain; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    )


@unit_bp.route("/<int:unit_id>/sentences/export")
@login_required
@admin_required
def sentence_export(unit_id):
    """Xuất toàn bộ câu của unit ra file .txt theo đúng định dạng import."""
    unit = UnitService.get_unit(unit_id)
    if not unit:
        flash("Bài học không tồn tại.", "danger")
        return redirect(url_for("course.list"))

    sentences = SentenceService.get_sentences_by_unit(unit_id)

    lines = []
    for s in sentences:
        if s.pronunciation:
            lines.append(f"Thuật ngữ: {s.content} ({s.pronunciation}) Nghĩa: {s.meaning}")
        else:
            lines.append(f"Thuật ngữ: {s.content} Nghĩa: {s.meaning}")

    content = "\n".join(lines)
    safe_name = unit.name.replace(" ", "_") if unit.name else f"unit_{unit_id}"
    filename = f"sentences_{safe_name}.txt"
    encoded_filename = urllib.parse.quote(filename)

    return Response(
        content,
        mimetype="text/plain; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    )



@unit_bp.route("/<int:unit_id>/flashcards/study")
@login_required
def flashcards_study(unit_id):
    """Study mode for flashcards."""
    unit = UnitService.get_unit(unit_id)
    if not unit:
        flash("Bài học không tồn tại.", "danger")
        return redirect(url_for("course.list"))
        
    flashcards = FlashcardService.get_flashcards_with_status(unit_id, current_user.id)
    progress = FlashcardService.get_unit_progress(unit_id, current_user.id)
    return render_template("units/flashcards_study.html", unit=unit, flashcards=flashcards, progress=progress)

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

@unit_bp.route("/<int:unit_id>/flashcards/progress", methods=["POST"])
@login_required
def update_flashcard_progress(unit_id):
    """API to update user progress for a unit's flashcards."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid request"}), 400
        
    last_card_id = data.get('lastFlashcardId')
    is_random = data.get('isRandom')
    
    result = FlashcardService.update_unit_progress(unit_id, current_user.id, last_card_id, is_random)
    
    if result["success"]:
        return jsonify(result), 200
    return jsonify(result), 400

@unit_bp.route("/<int:unit_id>/test")
@login_required
def test_study(unit_id):
    """Test practice mode for a unit."""
    unit = UnitService.get_unit(unit_id)
    if not unit:
        flash("Bài học không tồn tại.", "danger")
        return redirect(url_for("course.list"))
        
    result = TestService.generate_test(unit_id)
    if not result["success"]:
        flash(result["message"], "danger")
        return redirect(url_for("unit.detail", unit_id=unit_id))
        
    record = TestService.get_record(current_user.id, unit_id)
    
    return render_template("units/test.html", unit=unit, questions=result["questions"], record=record)

@unit_bp.route("/<int:unit_id>/test/result", methods=["POST"])
@login_required
def save_test_result(unit_id):
    """API to save test result."""
    data = request.get_json()
    if not data or 'score' not in data or 'time' not in data:
        return jsonify({"success": False, "message": "Invalid request"}), 400
        
    score = float(data['score'])
    completion_time = int(data['time'])
    
    result = TestService.save_result(current_user.id, unit_id, score, completion_time)
    
    if result["success"]:
        return jsonify(result), 200
    return jsonify(result), 400

@unit_bp.route("/handwriting", methods=["POST"])
@login_required
def handwriting_proxy():
    """Proxy for handwriting recognition API."""
    data = request.get_json()
    if not data or 'ink' not in data:
        return jsonify({"success": False, "message": "Invalid request"}), 400
        
    payload = {
        "options": "enable_pre_space",
        "requests": [{
            "writing_guide": {"writing_area_width": 400, "writing_area_height": 150},
            "ink": data['ink'],
            "language": data.get('lang', 'zh_CN')
        }]
    }
    
    try:
        url = "https://www.google.com/inputtools/request?ime=handwriting&app=mobilesearch&cs=1&oe=UTF-8"
        import requests
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        return jsonify(response.json()), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
