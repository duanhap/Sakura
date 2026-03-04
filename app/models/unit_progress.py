from app.extensions import db

class UnitProgress(db.Model):
    __tablename__ = "unitprogress"

    id = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    UnitId = db.Column(db.Integer, db.ForeignKey("unit.id"), nullable=False)
    lastFlashcardId = db.Column(db.Integer, db.ForeignKey("flashcard.id"), nullable=True)
    isRandom = db.Column(db.Boolean, default=False)

    __table_args__ = (db.UniqueConstraint('UserId', 'UnitId', name='unique_user_unit_progress'),)

    user = db.relationship("User")
    unit = db.relationship("Unit")
    flashcard = db.relationship("Flashcard")
