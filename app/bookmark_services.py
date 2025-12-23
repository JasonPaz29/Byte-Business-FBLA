from app import db
from app.models import BookMark

def add_bookmark(user_id, business_id):
    existing = BookMark.query.filter_by(user_id=user_id, business_id=business_id).first()
    if existing:
        return False
    
    bookmark = BookMark(user_id=user_id, business_id=business_id)

    db.session.add(bookmark)
    db.session.commit()
    return True

def remove_bookmark(user_id, business_id):
    existing = BookMark.query.filter_by(user_id=user_id, business_id=business_id).first()

    if not existing:
        return False
    
    db.session.delete(existing)
    db.session.commit()
    return True
