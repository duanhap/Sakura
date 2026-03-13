from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.models import Unit, Reading
import os

app = create_app()


with app.app_context():
    units = Unit.query.all()
    print(f"Total units: {len(units)}")
    for u in units:
        readings = u.readings.all()
        if len(readings) > 0:
            print(f"Unit {u.id} ({u.name}): {len(readings)} readings")
            for r in readings:
                print(f"  - Reading {r.id}: {r.title}, videoUrl: '{r.videoUrl}'")
