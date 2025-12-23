import requests
from flask import request, current_app

def verify_turnstile() -> bool:
    token = request.form.get("cf-turnstile-response", "")
    secret = current_app.config.get("TURNSTILE_SECRET_KEY")

    if not token:
        print("Turnstile: missing token")
        return False
    if not secret:
        print("Turnstile: missing secret key in config")
        return False

    try:
        data = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": secret,
                "response": token,
                # DO NOT send remoteip while debugging
            },
            timeout=5
        ).json()
        print("Turnstile response:", data)
    except Exception as e:
        print("Turnstile exception:", e)
        return False

    return bool(data.get("success"))
