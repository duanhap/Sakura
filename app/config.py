import os

class Config:
    SECRET_KEY = os.getenv("SAKURA_SECRET_KEY")

    DB_USER = os.getenv("SAKURA_DB_USER")
    DB_PWD = os.getenv("SAKURA_DB_PASSWORD")
    DB_HOST = os.getenv("SAKURA_DB_HOST")
    DB_PORT = os.getenv("SAKURA_DB_PORT", "3306")
    DB_NAME = os.getenv("SAKURA_DB_NAME")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PWD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False