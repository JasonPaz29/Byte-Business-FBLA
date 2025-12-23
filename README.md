# Byte Business

## Overview
Byte Business is a local business discovery platform that allows users to browse businesses by category, save bookmarks, leave reviews and ratings, and view promotional deals. The application focuses on usability, data integrity, and modular backend design.

---

## FBLA Prompt Feature Mapping

| Requirement | Feature | Location |
|---|---|---|
| Business listings | Category-based filtering | Home page |
| Reviews & ratings | User review system with star ratings | Business detail page |
| Deals & coupons | Business-linked promotional deals | Business detail page |
| Bot prevention | Cloudflare Turnstile CAPTCHA | Registration |
| Bookmarks | Saved businesses per user | Bookmarks page |
| Data storage | Relational database (SQLAlchemy + SQLite) | Models |
| Presentable output | Printable PDF bookmark report with summary statistics | Bookmarks page |
| Intelligent feature | Personalized business recommendations based on user preferences | Home page |

---

## Tech Stack
- Python (Flask)
- SQLAlchemy ORM
- SQLite database
- Cloudflare Turnstile (bot prevention)

---

## Environment Variables

This project uses environment variables for configuration.  
Create a `.env` file in the project root with the following values:

FLASK_ENV=development  
FLASK_APP=run.py  
SECRET_KEY=your_secret_key_here  
TURNSTILE_SITE_KEY=your_turnstile_site_key  
TURNSTILE_SECRET_KEY=your_turnstile_secret_key

---

## Setup Instructions
1. Create a virtual environment  
   `python3 -m venv .venv`
2. Install dependencies  
   `pip install -r requirements.txt`
3. Initialize and apply database migrations  
   `flask db init`  
   `flask db migrate -m "initial migration"`  
   `flask db upgrade`
4. Seed sample data  
   `python3 seed_database.py`  
   `python3 seed_deals.py`  
   `python3 seed_reviews.py`
5. Run the application  
   `python3 run.py`

---

## Limitations & Future Improvements
- Business owner dashboards
- Production email verification
- Deployment to a live production environment
