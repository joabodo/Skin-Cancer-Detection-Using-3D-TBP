import pyotp

def generate_totp_secret():
    return pyotp.random_base32()


def get_totp_uri(email, secret, issuer_name="SkinAI"):
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer_name)


def verify_totp(secret, code):
    totp = pyotp.TOTP(secret)
    return totp.verify(code)
