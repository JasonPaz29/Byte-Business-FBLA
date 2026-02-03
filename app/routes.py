from flask import Blueprint, render_template, redirect, url_for, request, flash
from .extensions import db
from .models import User, Business, Review
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from flask_login import login_required, current_user
from .recommendations import recommended_businesses
from .profanity_check import contains_profanity, censor_text
from .email_service import send_verification_email

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
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
        flash("You must verify your email to submit a review.", "info")
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
        flash("You must verify your email to edit a review.", "info")
        return redirect(url_for("main.business_detail", business_id=review_id))
    review = Review.query.get_or_404(review_id)
    if not review:
        flash("That review does not exist.", "info")
        return redirect(url_for("main.business_detail", business_id=review.business_id))
    if review.user_id != current_user.id:
        flash("You can only edit your own reviews.", "info")
        return redirect(url_for("main.business_detail", business_id=review.business_id))
    return render_template('edit_review.html', review=review)


@main_bp.route('/reviews/<int:review_id>/edit', methods=['POST'])
@login_required
def update_review(review_id):
    review = Review.query.get_or_404(review_id)
    rating = int(request.form.get('rating', 0))
    comment = request.form.get('comment', '').strip()
    if rating < 1 or rating > 5:
        flash("Rating must be between 1 and 5.", "danger")
        return redirect(url_for('main.business_detail', business_id=review.business_id))
    if contains_profanity(comment):
        comment = censor_text(comment)
        flash("Your comment contained inappropriate language and has been censored.", "warning")

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
        flash("You are not the owner of this review!", "danger")
        return redirect(url_for("main.business_detail", business_id=review.business_id))
    db.session.delete(review)
    db.session.commit()
    flash("The review has been successfully deleted.", "info")
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
        flash("Your email is already verified.", "info")
        return redirect(url_for("main.list_businesses"))

    email_sent, message = send_verification_email(current_user)
    if email_sent:
        flash(message, "success")
    else:
        flash(message, "warning")
    return redirect(url_for("main.list_businesses"))
