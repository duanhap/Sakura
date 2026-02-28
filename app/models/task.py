from app.extensions import db


class Task(db.Model):
    __tablename__ = "task"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    isCompleted = db.Column(db.Boolean, nullable=False, default=False)

    Missionid = db.Column(db.Integer, db.ForeignKey("mission.id"), nullable=False)
    Unitid = db.Column(db.Integer, db.ForeignKey("unit.id"), nullable=True)

    mission = db.relationship("Mission", back_populates="tasks")
    unit = db.relationship("Unit", back_populates="tasks")
