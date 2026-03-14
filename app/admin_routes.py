from flask import Blueprint, render_template, redirect, url_for, request, flash
from .extensions import db
from .models import User, Business, Review, BusinessRequest
from flask_login import login_required, current_user
from datetime import datetime

admin_bp = Blueprint("admin", __name__)



@admin_bp.route("/business-requests/admin", methods=["GET"])
@login_required
def business_requests_admin():
    if not current_user.is_admin:
        flash("You do not have permission to view that page.", "error")
        return redirect(url_for("main.list_businesses"))
    requests = BusinessRequest.query.order_by(BusinessRequest.created_at.desc()).all()
    return render_template("business_requests.html", requests=requests)

@admin_bp.route("/business-requests/<int:request_id>/approve", methods=["POST"])
@login_required
def approve_business_request(request_id):
    if not current_user.is_admin:
        flash("You do not have permission to perform that action.", "error")
        return redirect(url_for("main.list_businesses"))
    business_request = BusinessRequest.query.get_or_404(request_id)
    if business_request.is_active == False and business_request.reviewed_at is not None:
        flash("This business request has already been reviewed.", "error")
        return redirect(url_for("admin.business_requests_admin"))
    notes = request.form.get("notes")
    existing_business = Business.query.filter(
        Business.name.ilike(business_request.business_name),
        Business.location.ilike(business_request.location)
    ).first()
    if existing_business:
        flash("That business already exists in the directory.", "error")
        return redirect(url_for("admin.business_requests_admin"))
    business = Business(
        name=business_request.business_name,
        location=business_request.location,
        address=business_request.address,
        category=business_request.category,
        logo_url=business_request.logo_url,
        description=business_request.description,
        website=business_request.website,
        contact=business_request.contact,
        hours=business_request.hours,
        owner_id=business_request.user_id
    )
    db.session.add(business)
    business_request.decision_notes = notes
    business_request.reviewed_at = datetime.utcnow()
    business_request.is_active = False
    db.session.commit()
    flash("The business has been successfully created.", "success")
    return redirect(url_for("main.list_businesses"))

@admin_bp.route("/business-requests/<int:request_id>/decline", methods=["POST"])
@login_required
def decline_business_request(request_id):
    if not current_user.is_admin:
        flash("You are not allowed to make this decision!", "error")
        return redirect(url_for("main.list_businesses"))
    
    business_request = BusinessRequest.query.get_or_404(request_id)
    if business_request.is_active == False and business_request.reviewed_at is not None:
        flash("This business request has already been reviewed.", "error")
        return redirect(url_for("admin.business_requests_admin"))
    notes = request.form.get("notes")
    reason_declined = request.form.get("reason_declined")
    
    business_request.decision_notes = notes
    business_request.reason_declined = reason_declined
    business_request.reviewed_at = datetime.utcnow()
    business_request.is_active = False
    db.session.commit()
    flash("The business request has been successfully declined.", "success")
    return redirect(url_for("admin.business_requests_admin"))

@admin_bp.route("/admin-dashboard", methods=["GET"])
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("You are not allowed on this route!", "error")
        return redirect(url_for("main.list_businesses"))
    
    users = User.query.all()
    reviews = Review.query.all()
    businesses = Business.query.all()
    business_requests = BusinessRequest.query.order_by(BusinessRequest.created_at.desc()).all()
    
    return render_template(
        "admin_dashboard.html",
        users=users,
        reviews=reviews,
        businesses=businesses,
        business_requests=business_requests
    )

@admin_bp.route("/reviews/<int:review_id>/admin-hide", methods=["GET", "POST"])
@login_required
def admin_hide_review(review_id):
    review = Review.query.get_or_404(review_id)
    if not current_user.is_admin:
        flash("You are not an admin!", "error")
        return redirect(url_for("main.business_detail", business_id=review.business_id))
    review.is_visible = False
    db.session.commit()
    flash("The review has been successfully hidden.", "success")
    next_page = request.args.get("next")
    if next_page:
        return redirect(next_page)
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route("/reviews/<int:review_id>/admin-show", methods=["POST"])
@login_required
def admin_show_review(review_id):
    review = Review.query.get_or_404(review_id)
    if not current_user.is_admin:
        flash("You are not an admin!", "error")
        return redirect(url_for("main.business_detail", business_id=review.business_id))
    review.is_visible = True
    db.session.commit()
    flash("The review is now visible.", "success")
    next_page = request.args.get("next")
    if next_page:
        return redirect(next_page)
    return redirect(url_for("admin.admin_dashboard"))
    
@admin_bp.route("/admin-deactivate-user/<int:user_id>", methods=["POST"])
@login_required
def admin_deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    if not current_user.is_admin:
        flash("You are not an admin!", "error")
        return redirect(url_for("main.list_businesses"))
    user.is_active = False
    db.session.commit()
    flash("The User has been successfully deactivated.", "success")
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/admin-activate-user/<int:user_id>", methods=["POST"])
@login_required
def admin_activate_user(user_id):
    user = User.query.get_or_404(user_id)
    if not current_user.is_admin:
        flash("You are not an admin!", "error")
        return redirect(url_for("main.list_businesses"))
    user.is_active = True
    db.session.commit()
    flash("The User has been successfully activated.", "success")
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route("/admin-deactivate-business/<int:business_id>", methods=["POST"])
@login_required
def admin_deactivate_business(business_id):
    business = Business.query.get_or_404(business_id)
    if not current_user.is_admin:
        flash("You are not an admin!", "error")
        return redirect(url_for("main.list_businesses"))
    business.is_active = False
    db.session.commit()
    flash("The business has been successfully deactivated.", "success")
    next_page = request.args.get("next")
    if next_page:
        return redirect(next_page)
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/admin-activate-business/<int:business_id>", methods=["POST"])
@login_required
def admin_activate_business(business_id):
    business = Business.query.get_or_404(business_id)
    if not current_user.is_admin:
        flash("You are not an admin!", "error")
        return redirect(url_for("main.list_businesses"))
    business.is_active = True
    db.session.commit()
    flash("The business has been successfully activated.", "success")
    next_page = request.args.get("next")
    if next_page:
        return redirect(next_page)
    return redirect(url_for("admin.admin_dashboard"))
