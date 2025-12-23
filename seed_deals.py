import random
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models import Business, Deal  # adjust import paths if needed


DEAL_TEMPLATES = [
    ("10% Off First Visit", "Enjoy 10% off your first purchase. Mention this deal at checkout."),
    ("Buy One Get One 50% Off", "Buy one item, get the second item 50% off. Limited time."),
    ("Free Small Coffee", "Get a free small coffee with any breakfast sandwich purchase."),
    ("$5 Off $25+", "Save $5 when you spend $25 or more. Valid in-store only."),
    ("Student Discount", "Show a student ID for 15% off your order."),
    ("Happy Hour Special", "Happy hour pricing on select items from 3–6 PM."),
    ("Free Appetizer", "Free appetizer with purchase of 2 entrées. Dine-in only."),
    ("Weekend Deal", "10% off on Saturdays and Sundays."),
    ("New Customer Bonus", "New customers get a free add-on with purchase."),
    ("Seasonal Special", "Limited seasonal offer—ask staff for details."),
]

def seed_deals(min_deals=0, max_deals=2, chance_of_deal=0.55):
    businesses = Business.query.all()
    created = 0
    
    for business in businesses:
        if random.random() > chance_of_deal:
            continue
        
        amount_of_deals = random.randint(min_deals, max_deals)
        
        if amount_of_deals == 0:
            continue
        
        deals = random.sample(DEAL_TEMPLATES, k=min(amount_of_deals, len(DEAL_TEMPLATES)))
        
        for title, desc in deals:
            end_date = datetime.utcnow() + timedelta(days=random.randint(7, 30))
            deal = Deal(business_id=business.id,
                        title=title,
                        description=desc,
                        end_date=end_date
                        )
            db.session.add(deal)
            created += 1
    
    db.session.commit()
    print(f"Successfully created {created} deals across {len(businesses)} businesses!")
    
def clear_deals():
    deleted = Deal.query.delete()
    db.session.commit()
    print(f"Successfully deleted all {deleted} deals!")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        clear_deals()
        seed_deals()
    