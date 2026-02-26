from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.services import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("user.dashboard"))
    
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        
        user = AuthService.login(email, password)
        if user:
            login_user(user)
            flash("Đăng nhập thành công.", "success")
            # Send admin users to admin dashboard, others to user dashboard
            if user.role == "ADMIN":
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("user.dashboard"))
        flash("Email hoặc mật khẩu không đúng.", "danger")
    
    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Đã đăng xuất.", "info")
    return redirect(url_for("auth.login"))
