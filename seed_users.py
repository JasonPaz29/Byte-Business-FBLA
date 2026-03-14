from app import create_app
from app.extensions import db
from app.models import User
from werkzeug.security import generate_password_hash

USERS = {
    "john_doe": {"email": "john.doe@example.com"},
    "jane_smith": {"email": "jane.smith@example.com"},
    "maria_lopez": {"email": "maria.lopez@example.com"},
    "ethan_clark": {"email": "ethan.clark@example.com"},
    "olivia_turner": {"email": "olivia.turner@example.com"},
    "noah_wilson": {"email": "noah.wilson@example.com"},
    "ava_hall": {"email": "ava.hall@example.com"},
    "liam_carter": {"email": "liam.carter@example.com"},
    "sophia_brooks": {"email": "sophia.brooks@example.com"},
    "jackson_cole": {"email": "jackson.cole@example.com"},
    "mia_bennett": {"email": "mia.bennett@example.com"},
    "logan_price": {"email": "logan.price@example.com"},
}

DEFAULT_PASSWORD = "Password123!"


def seed_users():
    created = 0
    for username, info in USERS.items():
        exists = User.query.filter(
            (User.username == username) | (User.email == info["email"])
        ).first()
        if exists:
            continue

        user = User(
            username=username,
            email=info["email"],
            password=generate_password_hash(DEFAULT_PASSWORD, method="pbkdf2:sha256"),
            is_verified=True,
        )
        db.session.add(user)
        created += 1

    db.session.commit()
    print(f"Successfully created {created} users!")

def clear_users():
    deleted = User.query.delete()
    db.session.commit()
    print(f"Successfully deleted all {deleted} users!")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        clear_users()
        seed_users()
