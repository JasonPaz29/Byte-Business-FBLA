from flask import Blueprint, render_template, redirect, url_for, request, flash
from .extensions import db, login_manager
from datetime import datetime
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from flask_login import login_user, logout_user, login_required, current_user
from .security import verify_turnstile
from .verify_user import verify_email_token
from .email_service import send_verification_email
from .profanity_check import contains_profanity

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('main.home'))

@auth_bp.route('/verify_email/<token>')
def verify_email(token):
    email = verify_email_token(token)
    if not email:
        flash("Invalid or expired token.", "error")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("auth.login"))
    
    user.is_verified = True
    user.verified_at = datetime.utcnow()
    db.session.commit()
    flash("Email verified successfully!", "success")
    return redirect(url_for("main.list_businesses"))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash("You are already logged in.", "error")
        return redirect(url_for("main.list_businesses"))
    if request.method == 'POST':
        if not verify_turnstile():
            flash("Verification failed. Please try again.", "error")
            return render_template("auth/register.html")
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Username or email already exists.", "error")
            return redirect(url_for('auth.register'))
        
        if contains_profanity(username):
            flash("Username contains inappropriate language. Please choose another.", "error")
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        email_sent, message = send_verification_email(user)
        if email_sent:
            flash(message, "info")
        else:
            flash(f"{message} You can try again after logging in.", "warning")

        flash("Registration successful. Please log in.", "success")

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("main.list_businesses"))
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter(or_(User.username == identifier, User.email.ilike(identifier))).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("main.list_businesses"))
        flash("Incorrect Username/Email or Password", "error")

    return render_template("auth/login.html")
