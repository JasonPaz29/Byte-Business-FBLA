from datetime import datetime
import math
from flask import current_app, url_for
from flask_mail import Message

from .extensions import db, mail
from .verify_user import generate_email_token, generate_forgot_password_token

COOLDOWN_SECONDS = 60


def _cooldown_remaining_seconds(user) -> int:
    last_sent = getattr(user, "last_verification_email_sent_at", None)
    if not last_sent:
        return 0
    elapsed = (datetime.utcnow() - last_sent).total_seconds()
    if elapsed < 0:
        return COOLDOWN_SECONDS
    if elapsed >= COOLDOWN_SECONDS:
        return 0
    return max(0, math.ceil(COOLDOWN_SECONDS - elapsed))


def send_verification_email(user):
    if user.is_verified:
        return False, "Your email is already verified."

    if not current_app.config.get("MAIL_SERVER"):
        return False, "Email service is not configured. Please try again later."

    remaining = _cooldown_remaining_seconds(user)
    if remaining > 0:
        return False, f"Please wait {remaining} seconds before requesting another verification email."

    token = generate_email_token(user.email)
    verify_url = url_for("auth.verify_email", token=token, _external=True)

    subject = "Verify your Byte Business email"
    body = (
        "Welcome to Byte Business!\n\n"
        "Please verify your email by clicking the link below (valid for 1 hour):\n"
        f"{verify_url}\n\n"
        "If you did not create this account, you can ignore this email."
    )
    message = Message(subject=subject, recipients=[user.email], body=body)

    try:
        mail.send(message)
    except Exception:
        current_app.logger.exception("Failed to send verification email.")
        return False, "We could not send the verification email. Please try again."

    user.last_verification_email_sent_at = datetime.utcnow()
    try:
        db.session.commit()
    except Exception:
        current_app.logger.exception("Failed to update verification email timestamp.")
        db.session.rollback()
        return False, "We could not update your verification status. Please try again."

    return True, "Verification email sent! Please check your inbox."


def send_forgot_password_email(user):
    if not current_app.config.get("MAIL_SERVER"):
        return False, "Email service is not configured. Please try again later."

    remaining = _cooldown_remaining_seconds(user)
    if remaining > 0:
        return False, f"Please wait {remaining} seconds before requesting another verification email."

    token = generate_forgot_password_token(user.email)
    verify_url = url_for("auth.verify_forgot_password", token=token, _external=True)

    subject = "Reset your Byte Business password"
    body = (
        "Welcome to Byte Business!\n\n"
        "Please click on the link below to reset your password (valid for 1 hour):\n"
        f"{verify_url}\n\n"
        "If you did not reset the password, you can ignore this email."
    )
    message = Message(subject=subject, recipients=[user.email], body=body)

    try:
        mail.send(message)
    except Exception:
        current_app.logger.exception("Failed to send verification email.")
        return False, "We could not send the reset password email. Please try again."

    user.last_verification_email_sent_at = datetime.utcnow()
    try:
        db.session.commit()
    except Exception:
        current_app.logger.exception("Failed to update verification email timestamp.")
        db.session.rollback()
        return False, "We could not update your password. Please try again."

    return True, "Reset password email sent! Please check your inbox."


def send_deal_receipt_info(user):
    if not current_app.config.get("MAIL_SERVER"):
        return False, "Email service is not configured. Please try again later."

    remaining = _cooldown_remaining_seconds(user)
    if remaining > 0:
        return False, f"Please wait {remaining} seconds before requesting another receipt email."

    latest_redemption = None
    if getattr(user, "redeemed_deals", None):
        latest_redemption = max(
            user.redeemed_deals,
            key=lambda redeemed_deal: redeemed_deal.redeemed_at or datetime.min,
        )

    business_name = "Unavailable"
    deal_name = "Unavailable"
    redeemed_at_text = "Unavailable"
    if latest_redemption:
        if getattr(latest_redemption, "deal", None):
            deal_name = latest_redemption.deal.title or "Unavailable"
            business_name = latest_redemption.deal.business.name or "Unavailable"
        if latest_redemption.redeemed_at:
            redeemed_at_text = latest_redemption.redeemed_at.strftime("%B %d, %Y at %I:%M %p UTC")

    subject = "Byte Business Deal Info"
    body = (
        "Dear Customer,\n\n"
        "Thank you for using Byte Business. This email serves as your formal receipt "
        "and confirmation that your deal was successfully redeemed.\n\n"
        f"Business Name: {business_name}\n"
        f"Deal Name: {deal_name}\n"
        f"Redeemed At: {redeemed_at_text}\n\n"
        "Please keep this message for your records. If you believe this redemption was "
        "made in error, please contact the business directly or reply to our support team.\n\n"
        "Sincerely,\n"
        "Byte Business"
    )
    message = Message(subject=subject, recipients=[user.email], body=body)

    try:
        mail.send(message)
    except Exception:
        current_app.logger.exception("Failed to send receipt email.")
        return False, "We could not send the deal receipt email. Please try again."

    user.last_verification_email_sent_at = datetime.utcnow()
    try:
        db.session.commit()
    except Exception:
        current_app.logger.exception("Failed to update verification email timestamp.")
        db.session.rollback()
        return False, "We could not send your deal receipt. Please try again."

    return True, "Your receipt is in your email inbox!"
