from flask import Blueprint, render_template, redirect, url_for, request, flash
from .extensions import db
from .models import User, Business, Review, BusinessRequest, ReviewImage, ReviewLike
from sqlalchemy import or_
from flask_login import login_required, current_user
from .recommendations import recommended_businesses
from .profanity_check import contains_profanity, censor_text
from .email_service import send_verification_email
from datetime import datetime
import cloudinary.uploader

main_bp = Blueprint('main', __name__)


ALLOWED_FORMATS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_IMAGES = 4


def submit_request(user):
    business_name = request.form.get('business_name', '').strip()
    location = request.form.get('location', '').strip()
    address = request.form.get('address', '').strip()
    category = request.form.get('category', '').strip()
    description = request.form.get('description', '').strip()
    website = request.form.get('website', '').strip()
    contact = request.form.get('contact', '').strip()
    hours = request.form.get('hours', '').strip()
    logo_url = request.form.get('logo_url', '').strip()

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
        logo_url=logo_url or None,
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

@main_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for("main.list_businesses"))
    return render_template('index.html')


@main_bp.route('/businesses')
@login_required
def list_businesses():
    if current_user.is_admin:
        businesses = Business.query.all()
    else:
        businesses = Business.query.filter_by(is_active=True).all()
    recommended = recommended_businesses(current_user, businesses)
    return render_template('businesses.html', businesses=businesses, recommended=recommended)

@main_bp.route('/businesses/<int:business_id>', methods=['GET'])
@login_required
def business_detail(business_id):
    business = Business.query.get_or_404(business_id)
    if not current_user.is_admin and not business.is_active:
        flash("This business is no longer active.", "error")
        return redirect(url_for("main.list_businesses"))
    if current_user.is_admin:
        reviews = Review.query.filter_by(business_id=business.id).all()
    else:
        reviews = Review.query.filter_by(business_id=business.id, is_visible=True).all()
    return render_template('business_detail.html', business=business, reviews=reviews)

@main_bp.route('/businesses/<int:business_id>/review', methods=["POST"])
@login_required
def submit_review(business_id):
    if not current_user.is_verified:
        flash("You must verify your email to submit a review.", "error")
        return redirect(url_for('main.business_detail', business_id=business_id))
    business = Business.query.get_or_404(business_id)
    try: 
        rating = int(request.form.get('rating', 0))
    except ValueError:
        flash("Invalid rating value.", "error")
        return redirect(url_for('main.business_detail', business_id=business.id))
    comment = request.form.get('comment', '').strip()

    images = [image for image in request.files.getlist("review_images") if image and image.filename]

    if len(images) > MAX_IMAGES:
        flash(f"You can upload a maximum of {MAX_IMAGES} images.", "error")
        return redirect(url_for("main.business_detail", business_id=business.id))

    for image in images:
        extension = image.filename.rsplit(".", 1)[-1].lower() if "." in image.filename else ""
        if extension not in ALLOWED_FORMATS:
            flash(f"Only the following image formats are allowed: {', '.join(sorted(ALLOWED_FORMATS))}.", "error")
            return redirect(url_for("main.business_detail", business_id=business.id))

        size = image.content_length
        if size is None:
            current_position = image.stream.tell()
            image.stream.seek(0, 2)
            size = image.stream.tell()
            image.stream.seek(current_position)
        if size > MAX_FILE_SIZE:
            flash("Each image must be less than 5MB in size.", "error")
            return redirect(url_for("main.business_detail", business_id=business.id))
        image.stream.seek(0)

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
    db.session.flush()
    uploaded_public_ids = []
    try:
        for image in images:
            res = cloudinary.uploader.upload(image, folder="byte-business/reviews")
            public_id = res.get("public_id")
            uploaded_public_ids.append(public_id)
            review_image = ReviewImage(
                review_id=review.id,
                image_url=res["secure_url"],
                public_id=public_id
            )
            db.session.add(review_image)
        db.session.commit()
    except Exception:
        db.session.rollback()
        for public_id in uploaded_public_ids:
            if not public_id:
                continue
            try:
                cloudinary.uploader.destroy(public_id)
            except Exception:
                pass
        flash("One or more images could not be uploaded. Please try again.", "warning")
        return redirect(url_for('main.business_detail', business_id=business.id))

    flash("Your review has been submitted.", "success")
    return redirect(url_for('main.business_detail', business_id=business.id))


@main_bp.route('/reviews/<int:review_id>/edit')
@login_required
def edit_review(review_id):
    if not current_user.is_verified:
        flash("You must verify your email to edit a review.", "error")
        return redirect(url_for("main.business_detail", business_id=review_id))
    review = Review.query.get_or_404(review_id)
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
    
    images = ReviewImage.query.filter_by(review_id=review.id).all()
    for image in images:
        try:
            cloudinary.uploader.destroy(image.public_id)
        except Exception:
            pass
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

@main_bp.route("/business-requests", methods=["GET"])
@login_required
def user_business_requests():
    requests = BusinessRequest.query.filter_by(user_id=current_user.id).order_by(BusinessRequest.created_at.desc()).all()
    return render_template("user_business_requests.html", requests=requests)


@main_bp.route("/stats")
@login_required
def stats():
    total_users = User.query.count()
    total_businesses = Business.query.count()
    total_reviews = Review.query.count()
    return render_template("stats.html", total_users=total_users, total_businesses=total_businesses, total_reviews=total_reviews)

@main_bp.route("/reviews/<int:review_id>/like", methods=["POST"])
@login_required
def like_review(review_id):
    review = Review.query.get_or_404(review_id)
    if not review.is_visible and not current_user.is_admin:
        flash("That review is not available.", "error")
        return redirect(url_for("main.list_businesses"))
    if review.user_id == current_user.id:
        flash("You cannot like your own review.", "error")
        return redirect(url_for("main.business_detail", business_id=review.business_id))
    
    existing_like = ReviewLike.query.filter_by(user_id=current_user.id, review_id=review.id).first()
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        flash("You have unliked the review.", "success")
    else:
        new_like = ReviewLike(user_id=current_user.id, review_id=review.id)
        db.session.add(new_like)
        db.session.commit()
        flash("You have liked the review.", "success")
    
    return redirect(url_for("main.business_detail", business_id=review.business_id))
