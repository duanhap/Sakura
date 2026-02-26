import os

class Config:
    SECRET_KEY = os.getenv("SAKURA_SECRET_KEY", "dev-secret-sakura")
    DB_USER = os.getenv("SAKURA_DB_USER", "root")
    DB_PWD = os.getenv("SAKURA_DB_PASSWORD", "duanhap2554")
    DB_HOST = os.getenv("SAKURA_DB_HOST", "localhost")
    DB_PORT = os.getenv("SAKURA_DB_PORT", "3306")
    DB_NAME = os.getenv("SAKURA_DB_NAME", "sakura")

    SQLALCHEMY_DATABASE_URI = f"mysql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
