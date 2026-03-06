from app.extensions import db
from datetime import date

class Grammar(db.Model):
    __tablename__ = "grammar"

    id = db.Column(db.Integer, primary_key=True)
    UnitId = db.Column(db.Integer, db.ForeignKey("unit.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    createdAt = db.Column(db.Date, nullable=False, default=date.today)

    unit = db.relationship("Unit", back_populates="grammars")
