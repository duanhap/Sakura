#!/usr/bin/env python
"""Entry point for the Sakura application."""

import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file if it exists
load_dotenv()

app = create_app()

# The home/index routes are already registered in the application factory
# to avoid definition conflicts. This file simply runs the app.


if __name__ == "__main__":
    with app.app_context():
        from app.extensions import db
        db.create_all()
    app.run(debug=True)
