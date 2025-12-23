from flask import Blueprint, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Deal, RedeemDeal, Business
from app import db

deal_bp = Blueprint('deal', __name__)

@deal_bp.route('/redeem/<int:business_id>/<int:deal_id>', methods=['POST'])
@login_required
def redeem_deal(business_id, deal_id):
    business = Business.query.get_or_404(business_id)
    deal = Deal.query.get_or_404(deal_id)
    if not deal:
        flash('Deal not found.', 'danger')
        return redirect(url_for('main.business_detail', business_id=business_id))
    if not business:
        flash("Business not found.", "danger")
        return redirect(url_for("main.home"))
    
    if check_if_redeemed(current_user.id, deal_id):
        flash("You have already redeemed this deal.", "danger")
        return redirect(url_for('main.business_detail', business_id=business_id))
    
    redeem_deal = RedeemDeal(user_id=current_user.id, deal_id=deal_id)
    db.session.add(redeem_deal)
    db.session.commit()
    flash('Deal redeemed successfully!', 'success')
    return redirect(url_for('main.business_detail', business_id=business_id))

def check_if_redeemed(user_id, deal_id) -> bool:
    return RedeemDeal.query.filter_by(user_id=user_id, deal_id=deal_id).first() is not None
    
    