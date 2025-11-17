import pyotp

def generate_totp_secret():
    return pyotp.random_base32()

def get_totp_uri(user_email, secret, issuer_name="SkinAI"):
    return pyotp.totp.TOTP(secret).provisioning_uri(name=user_email, issuer_name=issuer_name)

def verify_totp(secret, token):
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)
