from datetime import date, datetime, timezone
from flask_login import UserMixin
from app.extensions import db

DEFAULT_AVATAR = "https://i.postimg.cc/G3J4rgS8/tai-xuong-(76).jpg"
DEFAULT_WALLPAPER = "https://i.postimg.cc/13W6S7XB/tai-xuong-(77).jpg"

class User(db.Model, UserMixin):
    __tablename__ = "User"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255))
    description = db.Column(db.String(255))
    wallpaper = db.Column(db.String(255))
    role = db.Column(db.String(255), nullable=False, default="USER")
    createdAt = db.Column(db.Date, nullable=False, default=date.today)
    lastSeen = db.Column(db.DateTime, nullable=True)
    currentActivity = db.Column(db.String(255), nullable=True)

    missions = db.relationship("Mission", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    flashcard_statuses = db.relationship("FlashcardUser", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    @property
    def avatar_url(self) -> str:
        return self.avatar or DEFAULT_AVATAR

    @property
    def wallpaper_url(self) -> str:
        return self.wallpaper or DEFAULT_WALLPAPER

    @property
    def is_online(self) -> bool:
        """True nếu lastSeen trong vòng 5 phút gần đây."""
        if not self.lastSeen:
            return False
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return (now - self.lastSeen).total_seconds() < 300  # 5 phút

    @property
    def activity_label(self) -> str:
        """Trả về nhãn tiếng Việt mô tả hoạt động hiện tại."""
        activity_map = {
            "watching_video": "🎬 Đang xem video",
            "viewing_document": "📄 Đang xem tài liệu",
            "studying_flashcard": "📚 Học từ vựng",
            "taking_test": "📝 Làm bài kiểm tra",
            "browsing": "🌐 Đang duyệt web",
        }
        if not self.currentActivity:
            return "💤 Ngồi chơi"
        return activity_map.get(self.currentActivity, "💤 Ngồi chơi")
