from app.extensions import db

class FlashcardUser(db.Model):
    __tablename__ = "flashcarduser"

    id = db.Column(db.Integer, primary_key=True)
    FlashcardId = db.Column(db.Integer, db.ForeignKey("flashcard.id"), nullable=False)
    UserId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.Enum('CHUA_THUOC', 'THUOC'), nullable=False, default='CHUA_THUOC')

    flashcard = db.relationship("Flashcard", back_populates="user_status")
    user = db.relationship("User", back_populates="flashcard_statuses")
