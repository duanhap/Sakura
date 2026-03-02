from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from app.services import UserService

online_bp = Blueprint("online", __name__, url_prefix="/online")


@online_bp.route("/")
@login_required
def online_page():
    """Trang hiển thị danh sách user đang online (dành cho cả admin và user)."""
    return render_template("online_users.html")


@online_bp.route("/heartbeat", methods=["POST"])
@login_required
def heartbeat():
    """
    Frontend gọi endpoint này mỗi ~30 giây để cập nhật trạng thái online.
    Body JSON: { "activity": "browsing" }  (tùy chọn)
    """
    data = request.get_json(silent=True) or {}
    activity = data.get("activity", "browsing")

    # Chỉ chấp nhận các activity hợp lệ
    VALID_ACTIVITIES = {
        "browsing",
        "watching_video",
        "viewing_document",
        "studying_flashcard",
        "taking_test",
    }
    if activity not in VALID_ACTIVITIES:
        activity = "browsing"

    UserService.update_activity(current_user.id, activity)
    return jsonify({"status": "ok"})


@online_bp.route("/users", methods=["GET"])
@login_required
def get_online_users():
    """
    API trả về danh sách user online dưới dạng JSON.
    Cả admin lẫn user thường đều có thể gọi.
    """
    users = UserService.get_online_users()
    result = []
    for u in users:
        result.append({
            "id": u.id,
            "name": u.name,
            "avatar": u.avatar_url,
            "role": u.role,
            "activity": u.currentActivity or "browsing",
            "activity_label": u.activity_label,
        })
    return jsonify({"users": result, "count": len(result)})
