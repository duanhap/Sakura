from datetime import date
from app.extensions import db

class Course(db.Model):
    __tablename__ = "course"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255))
    description = db.Column(db.String(255), nullable=False)
    createdAt = db.Column(db.Date, nullable=False, default=date.today)

    units = db.relationship("Unit", back_populates="course", lazy="dynamic", cascade="all, delete-orphan")
