from datetime import date
from app.extensions import db


class Mission(db.Model):
    __tablename__ = "mission"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    createdAt = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(255))

    Userid = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", back_populates="missions")

    tasks = db.relationship("Task", back_populates="mission", lazy="dynamic", cascade="all, delete-orphan")
