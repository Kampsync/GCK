import secrets

def generate_token(length=16):
    return secrets.token_urlsafe(length)
