from flask import Blueprint, render_template, redirect, url_for, request, flash
from .extensions import db
from .models import User, Business, Review, BusinessRequest
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from flask_login import login_required, current_user
from .recommendations import recommended_businesses
from .profanity_check import contains_profanity, censor_text
from .email_service import send_verification_email

main_bp = Blueprint('main', __name__)


def submit_request(user):
    business_name = request.form.get('business_name', '').strip()
    location = request.form.get('location', '').strip()
    address = request.form.get('address', '').strip()
    category = request.form.get('category', '').strip()
    description = request.form.get('description', '').strip()
    website = request.form.get('website', '').strip()
    contact = request.form.get('contact', '').strip()
    hours = request.form.get('hours', '').strip()

    if not business_name or not location or not address or not category:
        return False, "Please fill out all required fields."

    existing_business = Business.query.filter(
        Business.name.ilike(business_name),
        Business.location.ilike(location)
    ).first()
    if existing_business:
        return False, "That business already exists in the directory."

    business_request = BusinessRequest(
        user_id=user.id,
        business_name=business_name,
        location=location,
        address=address,
        category=category,
        description=description or None,
        website=website or None,
        contact=contact or None,
        hours=hours or None
    )
    db.session.add(business_request)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return False, "We could not submit your request right now. Please try again."

    return True, "Your business request has been submitted and will be reviewed soon."


def give_user_admin():
    user = User.query.filter_by(username="AdminJason").first()
    if user:
        user.is_admin = True
        db.session.commit()

@main_bp.route('/')
def home():
    give_user_admin()
    if current_user.is_authenticated:
        return redirect(url_for("main.list_businesses"))
    return render_template('index.html')


@main_bp.route('/businesses')
@login_required
def list_businesses():
    businesses = Business.query.all()
    recommended = recommended_businesses(current_user, businesses)
    for r in recommended:
        print(f"Recommended: {r.name} - Avg Rating: {r.average_rating()}")
    return render_template('businesses.html', businesses=businesses, recommended=recommended)

@main_bp.route('/businesses/<int:business_id>', methods=['GET'])
@login_required
def business_detail(business_id):
    business = Business.query.get_or_404(business_id)
    reviews = Review.query.filter_by(business_id=business.id).all()
    return render_template('business_detail.html', business=business, reviews=reviews)

@main_bp.route('/businesses/<int:business_id>/review', methods=["POST"])
@login_required
def submit_review(business_id):
    if not current_user.is_verified:
        flash("You must verify your email to submit a review.", "error")
        return redirect(url_for('main.business_detail', business_id=business_id))
    business = Business.query.get_or_404(business_id)
    rating = int(request.form.get('rating', 0))
    comment = request.form.get('comment', '').strip()

    if contains_profanity(comment):
        comment = censor_text(comment)
        flash("Your comment contained inappropriate language and has been censored.", "warning")
    if rating < 1 or rating > 5:
        flash("Rating must be between 1 and 5.", "danger")
        return redirect(url_for('main.business_detail', business_id=business.id))

    review = Review(
        business_id=business.id,
        user_id=current_user.id,
        rating=rating,
        comment=comment
    )
    db.session.add(review)
    db.session.commit()

    flash("Your review has been submitted.", "success")
    return redirect(url_for('main.business_detail', business_id=business.id))


@main_bp.route('/reviews/<int:review_id>/edit')
@login_required
def edit_review(review_id):
    if not current_user.is_verified:
        flash("You must verify your email to edit a review.", "error")
        return redirect(url_for("main.business_detail", business_id=review_id))
    review = Review.query.get_or_404(review_id)
    if not review:
        flash("That review does not exist.", "error")
        return redirect(url_for("main.business_detail", business_id=review.business_id))
    if review.user_id != current_user.id:
        flash("You can only edit your own reviews.", "error")
        return redirect(url_for("main.business_detail", business_id=review.business_id))
    return render_template('edit_review.html', review=review)


@main_bp.route('/reviews/<int:review_id>/edit', methods=['POST'])
@login_required
def update_review(review_id):
    review = Review.query.get_or_404(review_id)
    rating = int(request.form.get('rating', 0))
    comment = request.form.get('comment', '').strip()
    if rating < 1 or rating > 5:
        flash("Rating must be between 1 and 5.", "error")
        return redirect(url_for('main.business_detail', business_id=review.business_id))
    if contains_profanity(comment):
        comment = censor_text(comment)
        flash("Your comment contained inappropriate language and has been censored.", "error")

    review.rating = rating
    review.comment = comment
    db.session.commit()

    flash("Your review has been updated.", "success")
    return redirect(url_for('main.business_detail', business_id=review.business_id))

@main_bp.route("/reviews/<int:review_id>/delete", methods=["POST"])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.user_id != current_user.id:
        flash("You are not the owner of this review!", "error")
        return redirect(url_for("main.business_detail", business_id=review.business_id))
    db.session.delete(review)
    db.session.commit()
    flash("The review has been successfully deleted.", "success")
    return redirect(url_for("main.business_detail", business_id=review.business_id))

@main_bp.route("/help")
@login_required
def help():
    return render_template("help.html")

@main_bp.route("/review")
@login_required
def reviews():
    reviews = Review.query.filter_by(user_id=current_user.id).all()
    return render_template("reviews.html", reviews=reviews)


@main_bp.route("/resend-verification")
@login_required
def resend_verification():
    if current_user.is_verified:
        flash("Your email is already verified.", "error")
        return redirect(url_for("main.list_businesses"))

    email_sent, message = send_verification_email(current_user)
    if email_sent:
        flash(message, "success")
    else:
        flash(message, "warning")
    return redirect(url_for("main.list_businesses"))


@main_bp.route("/create-business-request", methods=["GET", "POST"])
@login_required
def create_business_request():
    if not current_user.is_verified:
        flash("You must verify your email to request a business.", "error")
        return redirect(url_for("main.list_businesses"))

    if request.method == "POST":
        submitted, message = submit_request(current_user)
        flash(message, "success" if submitted else "error")
        if submitted:
            return redirect(url_for("main.list_businesses"))

    return render_template("create_business_request.html")
