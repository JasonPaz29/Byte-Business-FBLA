#TODO make these 4 routes on the double: owner/dashboard owner/business/edit owner/business/deals owner/business/stats or analytics
from flask import Blueprint, render_template, redirect, url_for, request, flash
from .extensions import db
from .models import Business, Review, Deal
from flask_login import login_required, current_user
from datetime import datetime

owner_bp = Blueprint("owner", __name__)

@owner_bp.route("/owner/businesses", methods=["GET"])
@login_required
def owned_businesses():
    businesses = Business.query.filter_by(owner_id=current_user.id).order_by(Business.created_at.desc()).all()
    return render_template("owner_businesses.html", businesses=businesses)

@owner_bp.route("/owner/dashboard/<int:business_id>", methods=["GET"])
@login_required
def owner_dashboard(business_id):
    business = Business.query.get_or_404(business_id)
    if current_user.id != business.owner_id:
        flash("You are not the owner of this business!", "error")
        return redirect(url_for("main.list_businesses"))
    return (render_template("owner_dashboard.html", business=business))

@owner_bp.route("/owner/business/<int:business_id>/edit", methods=["GET", "POST"])
@login_required
def edit_business(business_id):
    business = Business.query.get_or_404(business_id)
    if current_user.id != business.owner_id:
        flash("You are not the owner of this business!", "error")
        return redirect(url_for("main.list_businesses"))
    
    if request.method == "POST":
        business.name = request.form.get("name")
        business.location = request.form.get("location")
        business.address = request.form.get("address")
        business.category = request.form.get("category")
        business.description = request.form.get("description")
        business.website = request.form.get("website")
        business.contact = request.form.get("contact")
        business.hours = request.form.get("hours")
        
        db.session.commit()
        flash("Business details updated successfully!", "success")
        return redirect(url_for("owner.owner_dashboard", business_id=business.id))
    
    return render_template("edit_business.html", business=business)

@owner_bp.route("/owner/business/<int:business_id>/deals", methods=["GET"])
@login_required
def manage_deals(business_id):
    business = Business.query.get_or_404(business_id)
    if current_user.id != business.owner_id:
        flash("You are not the owner of this business!", "error")
        return redirect(url_for("main.list_businesses"))
    return render_template("manage_deals.html", business=business)

@owner_bp.route("/owner/business/<int:business_id>/add-deals", methods=["POST"])
@login_required
def owner_add_deals(business_id):
    business = Business.query.get_or_404(business_id)
    if current_user.id != business.owner_id:
        flash("You are not the owner of this business!", "error")
        return redirect(url_for("main.list_businesses"))
    
    deal_title = request.form.get("deal_title")
    deal_description = request.form.get("deal_description")
    deal_expiry = request.form.get("deal_expiry")
    
    if not deal_title or not deal_description or not deal_expiry:
        flash("All fields are required to add a deal.", "error")
        return redirect(url_for("owner.manage_deals", business_id=business.id))
    
    new_deal = Deal(
        title=deal_title,
        description=deal_description,
        end_date=datetime.strptime(deal_expiry, "%Y-%m-%d"),
        business_id=business.id
    )
    db.session.add(new_deal)
    db.session.commit()
    
    flash("New deal added successfully!", "success")
    return redirect(url_for("owner.manage_deals", business_id=business.id))

@owner_bp.route("/owner/business/<int:business_id>/<int:deal_id>/delete-deal", methods=["POST"])
@login_required
def owner_delete_deal(business_id, deal_id):
    business = Business.query.get_or_404(business_id)
    if current_user.id != business.owner_id:
        flash("You are not the owner of this business!", "error")
        return redirect(url_for("main.list_businesses"))
    
    deal = Deal.query.get_or_404(deal_id)
    if deal.business_id != business.id:
        flash("This deal does not belong to your business!", "error")
        return redirect(url_for("owner.manage_deals", business_id=business.id))
    
    db.session.delete(deal)
    db.session.commit()
    
    flash("Deal deleted successfully!", "success")
    return redirect(url_for("owner.manage_deals", business_id=business.id))

@owner_bp.route("/owner/business/<int:business_id>/stats", methods=["GET"])
@login_required
def business_stats(business_id):
    business = Business.query.get_or_404(business_id)
    if current_user.id != business.owner_id:
        flash("You are not the owner of this business!", "error")
        return redirect(url_for("main.list_businesses"))
    
    reviews = Review.query.filter_by(business_id=business.id).all()
    total_reviews = len(reviews)
    return render_template("business_stats.html", business=business, total_reviews=total_reviews)
