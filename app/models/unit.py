from datetime import date
from app.extensions import db


class Unit(db.Model):
    __tablename__ = "unit"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    video = db.Column(db.String(255))
    document = db.Column(db.String(255))
    createdAt = db.Column(db.Date, nullable=False, default=date.today)

    Courseid = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    course = db.relationship("Course", back_populates="units")

    tasks = db.relationship("Task", back_populates="unit", lazy="dynamic", cascade="all, delete-orphan")
    flashcards = db.relationship("Flashcard", back_populates="unit", lazy="dynamic", cascade="all, delete-orphan")
    sentences = db.relationship("Sentence", back_populates="unit", lazy="dynamic", cascade="all, delete-orphan")
    grammars = db.relationship("Grammar", back_populates="unit", lazy="dynamic", cascade="all, delete-orphan")
    readings = db.relationship("Reading", back_populates="unit", lazy="dynamic", cascade="all, delete-orphan")

