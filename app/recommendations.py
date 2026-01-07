from app.models import BookMark
from app.extensions import db

def recommended_businesses(user, businesses, limit=6):
    bookmarked_ids = {
        bid for (bid,) in db.session.query(BookMark.business_id)
                                 .filter(BookMark.user_id == user.id)
                                 .all()
    }
    scored = []
    
    for business in businesses:
        if business.id in bookmarked_ids:
            continue
        score = 0
        avg_rating = business.average_rating() or 0
        review_count = len(business.reviews) if hasattr(business, 'reviews') else 0
        
        score = (avg_rating * 2) + (review_count * 0.5)
        
        if getattr(business, "deals", None):
            score += 2
        
        scored.append((business, score))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    print(scored[:limit])
    return [business for business, _ in scored[:limit]]
