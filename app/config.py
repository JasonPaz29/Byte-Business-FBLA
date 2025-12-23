import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', "FBLA_Byte_Business_2025-26")
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///byte_business.db')
    SQLALCHEMY_DATABASE_TRACK_MODIFICATIONS = False
    TURNSTILE_SITE_KEY = os.environ.get("TURNSTILE_SITE_KEY")
    TURNSTILE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY")

