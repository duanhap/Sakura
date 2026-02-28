from datetime import date
from app.extensions import db

class Flashcard(db.Model):
    __tablename__ = "flashcard"

    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(255), nullable=False)
    pronunciation = db.Column(db.String(255))
    description = db.Column(db.String(255))
    memoryTip = db.Column(db.String(255))
    createdAt = db.Column(db.Date, nullable=False, default=date.today)

    UnitId = db.Column(db.Integer, db.ForeignKey("unit.id"), nullable=False)
    
    unit = db.relationship("Unit", back_populates="flashcards")
    user_status = db.relationship("FlashcardUser", back_populates="flashcard", lazy="dynamic", cascade="all, delete-orphan")
