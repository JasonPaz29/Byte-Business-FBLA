from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_email_token(email: str) -> str:
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt="email-verify")

def verify_email_token(token: str, max_age: int = 3600) -> str:
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt="email-verify", max_age=max_age)
        return email
    except:
        return None
