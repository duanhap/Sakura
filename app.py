from datetime import date
import os

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
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

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


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
        return redirect(url_for("admin_dashboard"))
    return redirect(url_for("user_dashboard"))


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


@app.route("/admin")
@login_required
def admin_dashboard():
    if not is_admin():
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return redirect(url_for("user_dashboard"))

    user_count = User.query.count()
    course_count = Course.query.count()
    mission_count = Mission.query.count()
    task_count = Task.query.count()
    users = User.query.order_by(User.createdAt.desc()).all()

    return render_template(
        "admin/dashboard.html",
        user_count=user_count,
        course_count=course_count,
        mission_count=mission_count,
        task_count=task_count,
        users=users,
    )


@app.route("/admin/courses")
@login_required
def admin_courses():
    if not is_admin():
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return redirect(url_for("home"))
    courses = Course.query.order_by(Course.createdAt.desc()).all()
    return render_template("admin/courses.html", courses=courses)


@app.route("/admin/courses/new", methods=["GET", "POST"])
@login_required
def admin_course_new():
    if not is_admin():
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return redirect(url_for("home"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        image = request.form.get("image", "").strip() or None
        if not name or not description:
            flash("Tên và mô tả khóa học không được để trống.", "danger")
        else:
            course = Course(name=name, description=description, image=image)
            db.session.add(course)
            db.session.commit()
            flash("Tạo khóa học thành công.", "success")
            return redirect(url_for("admin_courses"))
    return render_template("admin/course_form.html", course=None)


@app.route("/admin/courses/<int:course_id>/edit", methods=["GET", "POST"])
@login_required
def admin_course_edit(course_id):
    if not is_admin():
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return redirect(url_for("home"))
    course = Course.query.get_or_404(course_id)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        image = request.form.get("image", "").strip() or None
        if not name or not description:
            flash("Tên và mô tả khóa học không được để trống.", "danger")
        else:
            course.name = name
            course.description = description
            course.image = image
            db.session.commit()
            flash("Cập nhật khóa học thành công.", "success")
            return redirect(url_for("admin_courses"))
    return render_template("admin/course_form.html", course=course)


@app.route("/admin/courses/<int:course_id>/delete", methods=["POST"])
@login_required
def admin_course_delete(course_id):
    if not is_admin():
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return redirect(url_for("home"))
    course = Course.query.get_or_404(course_id)
    # Xóa task thuộc các unit của khóa học, sau đó xóa unit và khóa học
    units = course.units.all()
    for unit in units:
        Task.query.filter_by(Unitid=unit.id).delete()
    Unit.query.filter_by(Courseid=course.id).delete()
    db.session.delete(course)
    db.session.commit()
    flash("Đã xóa khóa học.", "info")
    return redirect(url_for("admin_courses"))


@app.route("/admin/courses/<int:course_id>/units/new", methods=["GET", "POST"])
@login_required
def admin_unit_new(course_id):
    if not is_admin():
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return redirect(url_for("home"))
    course = Course.query.get_or_404(course_id)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip() or None
        video = request.form.get("video", "").strip() or None
        document = request.form.get("document", "").strip() or None
        if not name:
            flash("Tên bài học không được để trống.", "danger")
        else:
            unit = Unit(
                name=name,
                description=description,
                video=video,
                document=document,
                course=course,
            )
            db.session.add(unit)
            db.session.commit()
            flash("Tạo bài học thành công.", "success")
            return redirect(url_for("admin_units", course_id=course.id))
    return render_template("admin/unit_form.html", course=course)


@app.route("/admin/courses/<int:course_id>/units")
@login_required
def admin_units(course_id):
    if not is_admin():
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return redirect(url_for("home"))
    course = Course.query.get_or_404(course_id)
    units = course.units.order_by(Unit.createdAt.asc()).all()
    return render_template("admin/units.html", course=course, units=units)


@app.route("/admin/units/<int:unit_id>/edit", methods=["GET", "POST"])
@login_required
def admin_unit_edit(unit_id):
    if not is_admin():
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return redirect(url_for("home"))
    unit = Unit.query.get_or_404(unit_id)
    course = unit.course
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip() or None
        video = request.form.get("video", "").strip() or None
        document = request.form.get("document", "").strip() or None
        if not name:
            flash("Tên bài học không được để trống.", "danger")
        else:
            unit.name = name
            unit.description = description
            unit.video = video
            unit.document = document
            db.session.commit()
            flash("Cập nhật bài học thành công.", "success")
            return redirect(url_for("admin_units", course_id=course.id))
    return render_template("admin/unit_form.html", course=course, unit=unit)


@app.route("/admin/units/<int:unit_id>/delete", methods=["POST"])
@login_required
def admin_unit_delete(unit_id):
    if not is_admin():
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return redirect(url_for("home"))
    unit = Unit.query.get_or_404(unit_id)
    course_id = unit.Courseid
    Task.query.filter_by(Unitid=unit.id).delete()
    db.session.delete(unit)
    db.session.commit()
    flash("Đã xóa bài học.", "info")
    return redirect(url_for("admin_units", course_id=course_id))


@app.route("/admin/missions")
@login_required
def admin_missions():
    if not is_admin():
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return redirect(url_for("home"))
    missions = Mission.query.order_by(Mission.createdAt.desc()).all()
    return render_template("admin/missions.html", missions=missions)


@app.route("/admin/missions/new", methods=["GET", "POST"])
@login_required
def admin_mission_new():
    if not is_admin():
        flash("Bạn không có quyền truy cập trang này.", "danger")
        return redirect(url_for("home"))
    users = User.query.all()
    units = Unit.query.all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip() or None
        user_id = request.form.get("user_id")
        unit_ids = request.form.getlist("unit_ids")
        if not name or not user_id:
            flash("Tên mission và người dùng không được để trống.", "danger")
        else:
            mission = Mission(
                name=name,
                description=description,
                Userid=int(user_id),
            )
            db.session.add(mission)
            db.session.flush()
            for uid in unit_ids:
                if not uid:
                    continue
                task = Task(
                    name=f"Hoàn thành bài học #{uid}",
                    isCompleted=False,
                    Missionid=mission.id,
                    Unitid=int(uid),
                )
                db.session.add(task)
            db.session.commit()
            flash("Tạo mission thành công.", "success")
            return redirect(url_for("admin_missions"))
    return render_template("admin/mission_form.html", users=users, units=units)


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

@app.route("/dashboard")
@login_required
def user_dashboard():
    courses = Course.query.order_by(Course.createdAt.desc()).limit(6).all()
    missions = (
        Mission.query.filter_by(Userid=current_user.id)
        .order_by(Mission.createdAt.desc())
        .all()
    )
    return render_template(
        "user/dashboard.html",
        courses=courses,
        missions=missions,
    )


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.name = request.form.get("name", current_user.name).strip()
        current_user.description = (
            request.form.get("description", current_user.description or "").strip()
            or None
        )
        avatar = request.form.get("avatar", "").strip()
        wallpaper = request.form.get("wallpaper", "").strip()
        current_user.avatar = avatar or None
        current_user.wallpaper = wallpaper or None
        db.session.commit()
        flash("Cập nhật hồ sơ thành công.", "success")
        return redirect(url_for("profile"))
    return render_template("user/profile.html")


@app.route("/courses")
@login_required
def courses():
    all_courses = Course.query.order_by(Course.createdAt.desc()).all()
    return render_template("courses/list.html", courses=all_courses)


@app.route("/courses/<int:course_id>")
@login_required
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    units = course.units.order_by(Unit.createdAt.asc()).all()
    return render_template("courses/detail.html", course=course, units=units)


@app.route("/missions")
@login_required
def missions():
    missions = (
        Mission.query.filter_by(Userid=current_user.id)
        .order_by(Mission.createdAt.desc())
        .all()
    )
    return render_template("missions/list.html", missions=missions)


@app.route("/missions/<int:mission_id>")
@login_required
def mission_detail(mission_id):
    mission = Mission.query.get_or_404(mission_id)
    if mission.Userid != current_user.id and not is_admin():
        flash("Bạn không có quyền xem mission này.", "danger")
        return redirect(url_for("missions"))
    tasks = mission.tasks.order_by(Task.id.asc()).all()
    total = len(tasks)
    completed = len([t for t in tasks if t.isCompleted])
    progress = int((completed / total) * 100) if total else 0
    return render_template(
        "missions/detail.html",
        mission=mission,
        tasks=tasks,
        progress=progress,
    )


@app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.mission.Userid != current_user.id and not is_admin():
        flash("Bạn không có quyền cập nhật task này.", "danger")
        return redirect(url_for("missions"))
    task.isCompleted = not task.isCompleted
    db.session.commit()
    flash("Cập nhật trạng thái task thành công.", "success")
    return redirect(url_for("mission_detail", mission_id=task.Missionid))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

