import csv
from app import create_app 
from app.extensions import db
from app.models import Business

app = create_app()

def seed_businesses_from_csv():
    with app.app_context():
        with open('data/businesses.csv', newline='', encoding='utf-8') as csvfile:
            business_reader = csv.DictReader(csvfile)
            for row in business_reader:
                exists = Business.query.filter_by(name=row['name'], address=row['address']).first()
                if not exists:
                    business = Business(
                        name=row['name'],
                        location = row['location'],
                        address=row['address'],
                        category=row['category'],
                        description=row['description'],
                        website=row['website'],
                        contact=row['contact'],
                        hours=row['hours']
                    )
                    db.session.add(business)
            db.session.commit()
        print("Database seeded with businesses from CSV.")
if __name__ == '__main__':
    seed_businesses_from_csv()