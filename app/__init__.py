from flask import Flask
from app.config import Config
from app.extensions import db, login_manager
from app.models import User


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    # Load configuration
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register user loader
    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    # Register context processor
    from app.utils import is_admin
    
    @app.context_processor
    def inject_globals():
        DEFAULT_AVATAR = "https://i.postimg.cc/G3J4rgS8/tai-xuong-(76).jpg"
        DEFAULT_WALLPAPER = "https://i.postimg.cc/13W6S7XB/tai-xuong-(77).jpg"
        return {
            "DEFAULT_AVATAR": DEFAULT_AVATAR,
            "DEFAULT_WALLPAPER": DEFAULT_WALLPAPER,
            "is_admin": is_admin,
        }

    # Register blueprints
    from app.controllers.auth_controller import auth_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.admin_mission_controller import admin_mission_bp
    from app.controllers.admin_task_controller import admin_task_bp
    from app.controllers.user_controller import user_bp
    from app.controllers.course_controller import course_bp
    from app.controllers.mission_controller import mission_bp
    from app.controllers.unit_controller import unit_bp
    from app.controllers.online_controller import online_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_mission_bp)
    app.register_blueprint(admin_task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(mission_bp)
    app.register_blueprint(unit_bp)
    app.register_blueprint(online_bp)

    # make Unitid column nullable if needed (silent on failure)
    from sqlalchemy import text
    try:
        with app.app_context():
            db.session.execute(text(
                "ALTER TABLE task MODIFY COLUMN Unitid INT NULL"
            ))
            db.session.commit()
    except Exception:
        pass

    # Add online-tracking columns to User table if not exist (silent on failure)
    migrations = [
        "ALTER TABLE `User` ADD COLUMN lastSeen DATETIME NULL",
        "ALTER TABLE `User` ADD COLUMN currentActivity VARCHAR(255) NULL",
    ]
    for sql in migrations:
        try:
            with app.app_context():
                db.session.execute(text(sql))
                db.session.commit()
        except Exception:
            pass

    # root/home route for redirection logic
    @app.route("/")
    def home():
        from flask_login import current_user
        from flask import redirect, url_for
        from app.utils import is_admin
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if is_admin():
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("user.dashboard"))

    return app
