from datetime import date
import os

from flask import Flask, render_template, redirect, url_for, request, flash
from app.extensions import db, login_manager
from flask_login import (
    login_user,
    logout_user,
    current_user,
    login_required,
    UserMixin,
)
from werkzeug.security import generate_password_hash, check_password_hash


DEFAULT_AVATAR = "https://i.postimg.cc/G3J4rgS8/tai-xuong-(76).jpg"
DEFAULT_WALLPAPER = "https://i.postimg.cc/13W6S7XB/tai-xuong-(77).jpg"


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SAKURA_SECRET_KEY", "dev-secret-sakura")

# MySQL connection (from HSK.ddl + conection.md)
DB_USER = os.getenv("SAKURA_DB_USER", "root")
DB_PWD = os.getenv("SAKURA_DB_PASSWORD", "duanhap2554")
DB_HOST = os.getenv("SAKURA_DB_HOST", "localhost")
DB_PORT = os.getenv("SAKURA_DB_PORT", "3306")
DB_NAME = os.getenv("SAKURA_DB_NAME", "sakura")

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"mysql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Register extensions with this app (use the shared instances)
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "auth.login"  # use blueprint endpoint

# Register controllers as blueprints so that we can keep
# template and controller code modular.  This mirrors the
# factory-based setup in `run.py` and `app/__init__.py`.
from app.controllers.auth_controller import auth_bp
from app.controllers.admin_controller import admin_bp
from app.controllers.admin_mission_controller import admin_mission_bp
from app.controllers.admin_task_controller import admin_task_bp
from app.controllers.user_controller import user_bp
from app.controllers.course_controller import course_bp
from app.controllers.mission_controller import mission_bp
from app.controllers.unit_controller import unit_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(admin_mission_bp)
app.register_blueprint(admin_task_bp)
app.register_blueprint(user_bp)
app.register_blueprint(course_bp)
app.register_blueprint(mission_bp)
app.register_blueprint(unit_bp)


class User(db.Model, UserMixin):
    __tablename__ = "User"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255))
    description = db.Column(db.String(255))
    wallpaper = db.Column(db.String(255))
    role = db.Column(db.String(255), nullable=False, default="USER")
    createdAt = db.Column(db.Date, nullable=False, default=date.today)

    missions = db.relationship("Mission", back_populates="user", lazy="dynamic")

    @property
    def avatar_url(self) -> str:
        return self.avatar or DEFAULT_AVATAR

    @property
    def wallpaper_url(self) -> str:
        return self.wallpaper or DEFAULT_WALLPAPER


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255))
    description = db.Column(db.String(255), nullable=False)
    createdAt = db.Column(db.Date, nullable=False, default=date.today)

    units = db.relationship("Unit", back_populates="course", lazy="dynamic")


class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    video = db.Column(db.String(255))
    document = db.Column(db.String(255))
    createdAt = db.Column(db.Date, nullable=False, default=date.today)

    Courseid = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    course = db.relationship("Course", back_populates="units")

    tasks = db.relationship("Task", back_populates="unit", lazy="dynamic")


class Mission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    createdAt = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(255))

    Userid = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    user = db.relationship("User", back_populates="missions")

    tasks = db.relationship("Task", back_populates="mission", lazy="dynamic")


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    isCompleted = db.Column(db.Boolean, nullable=False, default=False)

    Missionid = db.Column(db.Integer, db.ForeignKey("mission.id"), nullable=False)
    Unitid = db.Column(db.Integer, db.ForeignKey("unit.id"), nullable=False)

    mission = db.relationship("Mission", back_populates="tasks")
    unit = db.relationship("Unit", back_populates="tasks")


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))


def is_admin() -> bool:
    return bool(current_user.is_authenticated and current_user.role == "ADMIN")


@app.context_processor
def inject_globals():
    return {
        "DEFAULT_AVATAR": DEFAULT_AVATAR,
        "DEFAULT_WALLPAPER": DEFAULT_WALLPAPER,
        "is_admin": is_admin,
    }


@app.route("/")
def home():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    if is_admin():
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("user.dashboard"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Đăng nhập thành công.", "success")
            return redirect(url_for("home"))
        flash("Email hoặc mật khẩu không đúng.", "danger")
    return render_template("auth/login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Đã đăng xuất.", "info")
    return redirect(url_for("login"))


# The administration-related routes were moved into the
# `admin_controller`, `admin_mission_controller`, and
# `admin_task_controller` blueprints.  Those blueprints are
# registered at the top of this module, so you no longer need these
# hand-crafted route functions here.  Keeping them would create
# duplicate URL rules and maintenance headaches, therefore they were
# removed.

# mission edit/delete routes
@app.route("/admin/missions/<int:mission_id>/edit", methods=["GET", "POST"])
@login_required
def admin_mission_edit(mission_id):
    if not is_admin():
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return redirect(url_for("home"))
    mission = Mission.query.get_or_404(mission_id)
    users = User.query.all()
    units = Unit.query.all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip() or None
        user_id = request.form.get("user_id")
        if not name or not user_id:
            flash("Tên mission và người dùng không được để trống.", "danger")
        else:
            # use service for validation/logic
            result = MissionService.update_mission(mission_id, name=name, description=description, user_id=(None if user_id == 'ALL' else user_id))
            flash(result.get("message", ""), "success" if result.get("success") else "danger")
            if result.get("success"):
                return redirect(url_for("admin_mission_detail", mission_id=mission_id))
    return render_template("admin/mission_form.html", mission=mission, users=users, units=units)

@app.route("/admin/missions/<int:mission_id>/delete", methods=["POST"])
@login_required
def admin_mission_delete(mission_id):
    if not is_admin():
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return redirect(url_for("home"))
    result = MissionService.delete_mission(mission_id)
    flash(result.get("message", ""), "info" if result.get("success") else "danger")
    return redirect(url_for("admin_missions"))

@app.route("/admin/missions/<int:mission_id>")
@login_required
def admin_mission_detail(mission_id):
    if not is_admin():
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return redirect(url_for("home"))
    mission = Mission.query.get_or_404(mission_id)
    # load tasks
    tasks = Task.query.filter_by(Missionid=mission.id).order_by(Task.id.asc()).all()
    units = Unit.query.all()
    return render_template("admin/mission_detail.html", mission=mission, tasks=tasks, units=units)

@app.route("/admin/missions/<int:mission_id>/tasks/new", methods=["POST"])
@login_required
def admin_task_new(mission_id):
    if not is_admin():
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return redirect(url_for("home"))
    name = request.form.get("name", "").strip()
    unit_id = request.form.get("unit_id")
    result = MissionService.add_task(mission_id, name, unit_id)
    flash(result.get("message", ""), "success" if result.get("success") else "danger")
    return redirect(url_for("admin_mission_detail", mission_id=mission_id))

@app.route("/admin/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def admin_task_edit(task_id):
    if not is_admin():
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return redirect(url_for("home"))
    task = Task.query.get_or_404(task_id)
    units = Unit.query.all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        unit_id = request.form.get("unit_id")
        if not name:
            flash("Tên task không được để trống.", "danger")
        else:
            result = MissionService.update_task(task_id, name=name, unit_id=unit_id)
            flash(result.get("message", ""), "success" if result.get("success") else "danger")
            if result.get("success"):
                return redirect(url_for("admin_mission_detail", mission_id=task.Missionid))
    return render_template("admin/task_form.html", task=task, units=units)

@app.route("/admin/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def admin_task_delete(task_id):
    if not is_admin():
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return redirect(url_for("home"))
    task = Task.query.get_or_404(task_id)
    mission_id = task.Missionid
    result = MissionService.delete_task(task_id)
    flash(result.get("message", ""), "info" if result.get("success") else "danger")
    return redirect(url_for("admin_mission_detail", mission_id=mission_id))

@app.route("/admin/users/new", methods=["GET", "POST"])
@login_required
def admin_user_new():
    if not is_admin():
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return redirect(url_for("home"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "USER").strip().upper() or "USER"
        avatar = request.form.get("avatar", "").strip() or None
        wallpaper = request.form.get("wallpaper", "").strip() or None

        if not name or not email or not password:
            flash("Tên, email và mật khẩu không được để trống.", "danger")
        elif User.query.filter_by(email=email).first():
            flash("Email đã tồn tại trong hệ thống.", "danger")
        else:
            hashed = generate_password_hash(password)
            user = User(
                name=name,
                email=email,
                password=hashed,
                avatar=avatar,
                wallpaper=wallpaper,
                role=role,
            )
            db.session.add(user)
            db.session.commit()
            flash("Tạo tài khoản user thành công.", "success")
            return redirect(url_for("admin_dashboard"))
    return render_template("admin/user_form.html")

# legacy route definitions are kept here for compatibility but are
# superseded by the blueprint modules.  The blueprint versions are
# registered above, so all requests are handled by `course_bp`,
# `user_bp`, `mission_bp`, etc.  The old functions have been removed
# to avoid endpoint conflicts; you can delete this comment block once
# you're certain the blueprints are active.

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

