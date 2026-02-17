from flask import redirect, url_for, flash, render_template, request, Blueprint
from flask_login import login_required, current_user
from app.models import User
from app.extensions import db
from .verify_user import generate_forgot_password_token, verify_forgot_password_token
from .security import verify_turnstile
from .email_service import send_forgot_password_email

fp_bp = Blueprint("forgot_password", __name__)


@fp_bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        if not verify_turnstile():
            flash("Verification failed. Please try again.", "error")
            return render_template("forgot_password.html")
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            success, message = send_forgot_password_email(user)
            if not success:
                flash(message, "error")
            else:
                flash("If an account with that email exists, a password reset link has been sent.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("If an account with that email exists, a password reset link has been sent.", "success")
            return redirect(url_for("auth.login"))
    return render_template("forgot_password.html")

