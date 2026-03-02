from app.extensions import db
from datetime import datetime
import pytz

class ResultUnitTest(db.Model):
    __tablename__ = "resultunittest"

    id = db.Column(db.Integer, primary_key=True)
    Userid = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    Unitid = db.Column(db.Integer, db.ForeignKey("unit.id"), nullable=False)
    completionTime = db.Column(db.Integer, nullable=False) # In seconds
    correctPercentage = db.Column(db.Float, nullable=False)
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", backref="unit_test_results")
    unit = db.relationship("Unit", backref="unit_test_results")

    __table_args__ = (
        db.UniqueConstraint('Userid', 'Unitid', name='unique_user_unit'),
    )
