import random
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models import Review, User, Business

REVIEW_TEMPLATES = {
    5: [
        "Amazing service and great quality. Will be back!",
        "Loved it—everything was fresh and fast.",
        "Best spot in town. Highly recommend.",
    ],
    4: [
        "Really good overall, just a small wait.",
        "Great experience, would come again.",
        "Solid place with friendly staff.",
    ],
    3: [
        "It was fine. Nothing crazy but not bad.",
        "Average experience—might try again later.",
        "Decent, but room for improvement.",
    ],
    2: [
        "Not what I expected. Service was slow.",
        "Could be better—food was lukewarm.",
        "Had some issues; probably won’t return soon.",
    ],
    1: [
        "Bad experience. Would not recommend.",
        "Very disappointed overall.",
        "Not worth it.",
    ],
}

def seed_reviews(min_reviews=1, max_reviews=7, chance_of_review=0.85):
    users = User.query.all()
    businesses = Business.query.all()
    created = 0
    for business in businesses:
        if random.random() > chance_of_review:
            continue

        num_reviews = random.randint(min_reviews, max_reviews)
        for _ in range(num_reviews):
            user = random.choice(users)
            rating = random.randint(1, 5)
            comment = random.choice(REVIEW_TEMPLATES[rating])
            created_at = datetime.utcnow() - timedelta(days=random.randint(0, 120))
            review = Review(
                user_id=user.id,
                business_id=business.id,
                rating=rating,
                comment=comment,
                created_at=created_at
            )
            db.session.add(review)
            created += 1
    db.session.commit()
    print(f"✅ Created {created} new reviews for {len(businesses)} businesses")
def clear_reviews():
    deleted = Review.query.delete()
    db.session.commit()
    print(f"🧹 Deleted {deleted} existing reviews")
    
if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        clear_reviews()
        seed_reviews()