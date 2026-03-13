from app.extensions import db

class ReadingSubtitle(db.Model):
    __tablename__ = "reading_subtitle"

    id = db.Column(db.Integer, primary_key=True)
    ReadingId = db.Column(db.Integer, db.ForeignKey("reading.id"), nullable=False)
    startTime = db.Column(db.Integer, nullable=False) # In milliseconds
    endTime = db.Column(db.Integer, nullable=False)   # In milliseconds
    content = db.Column(db.Text, nullable=False)
    pronunciation = db.Column(db.Text)
    translation = db.Column(db.Text)

    reading = db.relationship("Reading", back_populates="subtitles")
