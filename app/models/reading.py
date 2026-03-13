from app.extensions import db
from datetime import date

class Reading(db.Model):
    __tablename__ = "reading"

    id = db.Column(db.Integer, primary_key=True)
    UnitId = db.Column(db.Integer, db.ForeignKey("unit.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Thuật ngữ
    pronunciation = db.Column(db.Text)          # Cách đọc
    translation = db.Column(db.Text)            # Dịch
    videoUrl = db.Column(db.String(255))        # Link youtube
    createdAt = db.Column(db.Date, nullable=False, default=date.today)

    unit = db.relationship("Unit", back_populates="readings")
    subtitles = db.relationship("ReadingSubtitle", back_populates="reading", lazy="dynamic", cascade="all, delete-orphan")

