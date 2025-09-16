import os
import random
import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash, check_password_hash

# Optional Twilio for SMS 2FA
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except Exception:
    TWILIO_AVAILABLE = False

# -------------------------
# Configuration (use env vars)
# -------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET', 'change-me-in-production')
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', f"sqlite:///{os.path.join(basedir,'app.db')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail config (example using Gmail SMTP or any SMTP)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')        # YOUR EMAIL
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')        # YOUR EMAIL APP PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

# Twilio config (optional)
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_FROM_PHONE = os.getenv('TWILIO_FROM_PHONE')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# -------------------------
# Models
# -------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), nullable=False)  # 'patient' | 'dermatologist' | 'admin'
    phone = db.Column(db.String(64), nullable=True)
    twofa_enabled = db.Column(db.Boolean, default=True)
    twofa_method = db.Column(db.String(16), default='email')  # 'email' or 'sms'
    # 2FA stored one-time code (simple approach). In production use ephemeral store (redis) or TOTP.
    twofa_code = db.Column(db.String(10), nullable=True)
    twofa_expires_at = db.Column(db.DateTime, nullable=True)

    def set_password(self, plaintext):
        self.password_hash = generate_password_hash(plaintext)

    def check_password(self, plaintext):
        return check_password_hash(self.password_hash, plaintext)

    def get_id(self):
        return str(self.id)

# Helper to create DB (run once)
@app.before_first_request
def create_tables():
    db.create_all()

# -------------------------
# Login loader
# -------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------------
# Role-required decorator
# -------------------------
def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if current_user.role != role:
                flash("Access denied: insufficient role permissions.", "danger")
                return redirect(url_for("index"))
            return func(*args, **kwargs)
        return wrapper
    return decorator

# -------------------------
# Utilities for sending email and sms
# -------------------------
def send_email(subject, recipients, html_body):
    if not app.config.get('MAIL_USERNAME'):
        # Fallback: print to console if no mail configured
        print("EMAIL NOT CONFIGURED. Email would be sent to:", recipients)
        print("Subject:", subject)
        print(html_body)
        return
    msg = Message(subject, recipients=[recipients] if isinstance(recipients, str) else recipients)
    msg.html = html_body
    mail.send(msg)

def send_sms(to_phone, body):
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_PHONE and TWILIO_AVAILABLE):
        # Fallback: print to console
        print("SMS NOT CONFIGURED. Would send to:", to_phone)
        print(body)
        return
    client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(from_=TWILIO_FROM_PHONE, to=to_phone, body=body)

# -------------------------
# Routes: Index / Dashboard
# -------------------------
@app.route('/')
def index():
    return render_template("base.html")

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

# -------------------------
# Registration (one route handling role parameter)
# -------------------------
@app.route('/register/<role>', methods=['GET', 'POST'])
def register(role):
    if role not in ('patient', 'dermatologist', 'admin'):
        flash("Invalid role", "danger")
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        phone = request.form.get('phone', None)
        # Basic validation
        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template('register.html', role=role)

        if User.query.filter_by(email=email).first():
            flash("User already exists. Please login.", "warning")
            return redirect(url_for('login'))

        user = User(email=email, role=role, phone=phone)
        user.set_password(password)
        user.twofa_enabled = True
        user.twofa_method = request.form.get('twofa_method', 'email')
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html', role=role)

# -------------------------
# Login -> triggers sending 2FA if enabled
# -------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        role_selected = request.form.get('role')  # role user claims to log in as

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid credentials", "danger")
            return render_template('login.html')

        # Validate role
        if role_selected and user.role != role_selected:
            flash("Role mismatch. Please select the correct role.", "danger")
            return render_template('login.html')

        # If 2FA enabled: generate code, send, and forward to 2FA input page
        if user.twofa_enabled:
            code = f"{random.randint(0, 999999):06d}"
            user.twofa_code = code
            user.twofa_expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
            db.session.commit()

            msg_body = f"Your login verification code is: {code} (valid 5 minutes)"
            if user.twofa_method == 'sms' and user.phone:
                send_sms(user.phone, msg_body)
            else:
                # send email by default
                send_email("Your 2FA login code", user.email, f"<p>{msg_body}</p>")

            # Store the user_id temporarily in session to complete 2FA
            session['pre_2fa_user_id'] = user.id
            session['pre_2fa_remember'] = 'remember' in request.form
            flash("A verification code has been sent. Enter it below.", "info")
            return redirect(url_for('twofa'))
        else:
            # No 2FA: login immediately
            login_user(user, remember='remember' in request.form)
            flash("Logged in successfully", "success")
            return redirect(url_for('dashboard'))
    return render_template('login.html')

# -------------------------
# 2FA verification route
# -------------------------
@app.route('/twofa', methods=['GET', 'POST'])
def twofa():
    preid = session.get('pre_2fa_user_id')
    if not preid:
        flash("No 2FA pending login.", "warning")
        return redirect(url_for('login'))
    user = User.query.get(preid)
    if not user:
        flash("Invalid session.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        now = datetime.datetime.utcnow()
        if user.twofa_code == code and user.twofa_expires_at and user.twofa_expires_at > now:
            # success
            login_user(user, remember=session.get('pre_2fa_remember', False))
            # clear 2FA data
            user.twofa_code = None
            user.twofa_expires_at = None
            db.session.commit()
            session.pop('pre_2fa_user_id', None)
            session.pop('pre_2fa_remember', None)
            flash("2FA successful, you are logged in.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid or expired code. Request a new login or try again.", "danger")
            return render_template('twofa.html')
    return render_template('twofa.html')

# -------------------------
# Logout
# -------------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for('index'))

# -------------------------
# Password reset request (sends email with token)
# -------------------------
@app.route('/reset-password-request', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            token = serializer.dumps(user.email, salt='password-reset-salt')
            reset_link = url_for('reset_password', token=token, _external=True)
            html = f"<p>Click the link to reset your password: <a href='{reset_link}'>{reset_link}</a></p><p>This link expires in 1 hour.</p>"
            send_email("Password reset request", user.email, html)
            flash("Password reset link sent to your email (if it exists).", "info")
        else:
            flash("If the email exists we will send a reset link.", "info")
        return redirect(url_for('login'))
    return render_template('reset_request.html')

# -------------------------
# Reset password endpoint
# -------------------------
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)  # 1 hour
    except SignatureExpired:
        flash("Reset link expired. Request a new one.", "danger")
        return redirect(url_for('reset_request'))
    except BadSignature:
        flash("Invalid reset link.", "danger")
        return redirect(url_for('reset_request'))

    user = User.query.filter_by(email=email).first_or_404()
    if request.method == 'POST':
        password = request.form.get('password')
        if not password or len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template('reset_password.html', token=token)
        user.set_password(password)
        db.session.commit()
        flash("Password reset successful. Please login.", "success")
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)

# -------------------------
# Admin-only example page
# -------------------------
@app.route('/admin')
@login_required
@role_required('admin')
def admin_page():
    return f"Hello Admin {current_user.email}"

# -------------------------
# Run app
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
