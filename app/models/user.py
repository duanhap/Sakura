from datetime import date
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

    missions = db.relationship("Mission", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    flashcard_statuses = db.relationship("FlashcardUser", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    @property
    def avatar_url(self) -> str:
        return self.avatar or DEFAULT_AVATAR

    @property
    def wallpaper_url(self) -> str:
        return self.wallpaper or DEFAULT_WALLPAPER
