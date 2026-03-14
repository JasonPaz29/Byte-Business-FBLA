from .extensions import db
from datetime import datetime, timedelta
from flask_login import UserMixin




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    verified_at = db.Column(db.DateTime, default=None)
    last_verification_email_sent_at = db.Column(db.DateTime, default=None)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    bookmarks = db.relationship("BookMark", back_populates="user", cascade="all, delete-orphan")
    reviews = db.relationship("Review", back_populates="user", cascade="all, delete-orphan")
    redeemed_deals = db.relationship("RedeemDeal", back_populates="user", cascade="all, delete-orphan")
    business_requests = db.relationship("BusinessRequest", back_populates="user", cascade="all, delete-orphan")
    review_likes = db.relationship("ReviewLike", back_populates="user", cascade="all, delete-orphan")

class Business(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    owner_id = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String(300), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    logo_url = db.Column(db.String(300), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    website = db.Column(db.String(300), nullable=True)
    contact = db.Column(db.String(50), nullable=True)
    hours = db.Column(db.String(200), nullable=True)

    bookmarks = db.relationship("BookMark", back_populates="business", cascade="all, delete-orphan")
    reviews = db.relationship("Review", back_populates="business", cascade="all, delete-orphan")
    deals = db.relationship("Deal", back_populates="business", cascade="all, delete-orphan")


    def average_rating(self):
        if not self.reviews:
            return None
        return round(sum(review.rating for review in self.reviews) / len(self.reviews), 1)
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_visible = db.Column(db.Boolean, default=True)

    user = db.relationship("User", back_populates="reviews")
    business = db.relationship("Business", back_populates="reviews")
    review_images = db.relationship("ReviewImage", back_populates="review", cascade="all, delete-orphan")
    likes = db.relationship("ReviewLike", back_populates="review", cascade="all, delete-orphan")

class BookMark(db.Model):
    __tablename__ = "bookmarks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='bookmarks')
    business = db.relationship('Business', back_populates='bookmarks')

    __table_args__ = (db.UniqueConstraint('user_id', 'business_id', name='uq_user_business_bookmark'),)



class Deal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_date = db.Column(db.DateTime, default=datetime.utcnow()+timedelta(days=7), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    business = db.relationship("Business", back_populates="deals")
    redeemed_deals = db.relationship("RedeemDeal", back_populates="deal", cascade="all, delete-orphan")

class RedeemDeal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deal.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    redeemed_at = db.Column(db.DateTime, default=datetime.utcnow)

    deal = db.relationship("Deal", back_populates="redeemed_deals")
    user = db.relationship("User", back_populates="redeemed_deals")


class BusinessRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    business_name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    logo_url = db.Column(db.String(300), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    website = db.Column(db.String(300), nullable=True)
    contact = db.Column(db.String(50), nullable=True)
    hours = db.Column(db.String(200), nullable=True)

    is_active = db.Column(db.Boolean, default=True)
    decision_notes = db.Column(db.Text, nullable=True)
    reviewed_at = db.Column(db.DateTime, default=None) 
    reason_declined = db.Column(db.Text, nullable=True)    
    
    user = db.relationship("User", back_populates="business_requests")
    

class ReviewImage(db.Model):
    __tablename__ = "review_images"
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey("review.id"), nullable=False)
    image_url = db.Column(db.String(300), nullable=False)
    public_id = db.Column(db.String(300), nullable=False)
    
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    review = db.relationship("Review", back_populates="review_images")
    
class ReviewLike(db.Model):
    __tablename__ = "review_likes"
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey("review.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    review = db.relationship("Review", back_populates="likes")
    user = db.relationship("User", back_populates="review_likes")

    __table_args__ = (db.UniqueConstraint('review_id', 'user_id', name='uq_review_user_like'),)