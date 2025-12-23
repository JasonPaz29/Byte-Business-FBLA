from app import create_app
from dotenv import load_dotenv
import os
load_dotenv()
print("SITE KEY:", os.environ.get("TURNSTILE_SITE_KEY"))
print("SECRET KEY:", os.environ.get("TURNSTILE_SECRET_KEY"))


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)