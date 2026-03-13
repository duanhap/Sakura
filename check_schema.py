from dotenv import load_dotenv
load_dotenv()
from app import create_app
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    from app.extensions import db
    inspector = inspect(db.engine)
    for table_name in inspector.get_table_names():
        print(f"Table: {table_name}")
        for column in inspector.get_columns(table_name):
            print(f"  Column: {column['name']} ({column['type']})")
