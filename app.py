import os
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import secrets
import string
import base64

# Import our models and forms
from models import db, User, Item, Category, Match, Report
from forms import RegistrationForm, LoginForm, ItemForm, ReportForm, ClaimForm, HODPasswordChangeForm

app = Flask(__name__)
# Git sync check
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key-123') 
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site_v3.db')
# Fix for Render's postgres database URL (starts with postgres:// but SQLAlchemy needs postgresql://)
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

from flask_migrate import Migrate

db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- HELPER FUNCTIONS ---
def save_picture(form_picture):
    """Saves uploaded image to static/uploads"""
    if not form_picture:
        return None
    filename = secure_filename(form_picture.filename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_hex = secrets.token_hex(4)
    final_name = f"{timestamp}_{random_hex}_{filename}"
    picture_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], final_name)
    form_picture.save(picture_path)
    return final_name

def save_base64_picture(data_url):
    """Saves a base64 camera capture to static/uploads"""
    if not data_url or ',' not in data_url:
        return None
    header, encoded = data_url.split(',', 1)
    ext = 'png'
    if 'jpeg' in header:
        ext = 'jpg'
    img_data = base64.b64decode(encoded)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_hex = secrets.token_hex(4)
    final_name = f"{timestamp}_{random_hex}_camera.{ext}"
    picture_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], final_name)
    with open(picture_path, 'wb') as f:
        f.write(img_data)
    return final_name

def find_matches(new_item):
    """Logic ported from Django utils.py"""
    target_type = 'FOUND' if new_item.type == 'LOST' else 'LOST'
    
    # Get candidates from DB
    potential_matches = Item.query.filter(Item.type == target_type, Item.status == 'OPEN', Item.category_id == new_item.category_id).all()
    
    new_keywords = set(new_item.title.lower().split()) | set(new_item.description.lower().split()) | set(new_item.location.lower().split())

    for potential in potential_matches:
        pot_keywords = set(potential.title.lower().split()) | set(potential.description.lower().split()) | set(potential.location.lower().split())
        
        common = new_keywords.intersection(pot_keywords)
        if len(common) > 0:
            score = len(common) * 10
            # Save Match
            match = Match(score=score, lost_item_id=new_item.id if new_item.type == 'LOST' else potential.id,
                          found_item_id=potential.id if new_item.type == 'LOST' else new_item.id)
            db.session.add(match)
    db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES ---

@app.route("/")
@app.route("/home")
def home():
    category_id = request.args.get('category', type=int)
    item_type = request.args.get('type')
    
    query = Item.query.filter_by(status='OPEN')
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if item_type and item_type != 'ALL':
        query = query.filter_by(type=item_type)
        
    items = query.order_by(Item.created_at.desc()).limit(20).all()
    categories = Category.query.all()
    return render_template('home.html', items=items, categories=categories)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        role = form.role.data if form.role.data else 'STUDENT'
        
        clean_username = form.username.data.strip()
        clean_email = form.email.data.strip().lower()
        
        user = User(username=clean_username, email=clean_email, password=hashed_pw, role=role, department=None)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        clean_username = form.username.data.strip()
        # Case insensitive lookup
        user = User.query.filter(User.username.ilike(clean_username)).first()
        
        if user and check_password_hash(user.password, form.password.data):
            if user.role == 'HOD':
                flash('HOD accounts must log in via the dedicated HOD Portal.', 'warning')
                return redirect(url_for('hod_login'))
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/hod_login", methods=['GET', 'POST'])
def hod_login():
    if current_user.is_authenticated:
        if current_user.role == 'HOD':
            return redirect(url_for('hod_dashboard'))
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            if user.role != 'HOD':
                flash('This portal is strictly for HODs. Please use standard login.', 'danger')
                return redirect(url_for('login'))
            login_user(user)
            return redirect(url_for('hod_dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('hod_login.html', title='HOD Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/post", methods=['GET', 'POST'])
@login_required
def post_item():
    form = ItemForm()
    # Populate categories dynamically
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]

    # Pre-fill from query params (e.g. if redirected from claim page)
    if request.method == 'GET':
        if request.args.get('type'):
            form.type.data = request.args.get('type')
        if request.args.get('category'):
            try:
                form.category.data = int(request.args.get('category'))
            except ValueError:
                pass
    
    if form.validate_on_submit():
        # Handle image: prefer camera capture, fall back to file upload
        camera_data = request.form.get('camera_image')
        
        # MANDATORY IMAGE CHECK
        if not camera_data and not form.image.data:
            flash('You must provide an image (upload or camera) to post an item.', 'danger')
            return render_template('post_item.html', title='Post Item', form=form)

        if camera_data:
            pic_file = save_base64_picture(camera_data)
        else:
            pic_file = save_picture(form.image.data)

        # Parse spatial data
        lat = request.form.get('latitude')
        lng = request.form.get('longitude')
        try:
            lat = float(lat)
            lng = float(lng)
        except (TypeError, ValueError):
            lat = None
            lng = None

        item = Item(title=form.title.data, type=form.type.data, description=form.description.data,
                    location=form.location.data, latitude=lat, longitude=lng, date_occurred=form.date_occurred.data,
                    user_id=current_user.id, category_id=form.category.data, image_file=pic_file,
                    contact_name=form.contact_name.data, contact_number=form.contact_number.data,
                    is_high_value=form.is_high_value.data, assigned_department=form.assigned_department.data)
        
        # Generate verification code ONLY for LOST items
        if form.type.data == 'LOST':
            alphabet = string.ascii_uppercase + string.digits
            while True:
                code = ''.join(secrets.choice(alphabet) for i in range(8))
                if not Item.query.filter_by(verification_code=code).first():
                    break
            item.verification_code = code
        else:
            item.verification_code = None

        db.session.add(item)
        db.session.commit()
        
        # Trigger matching logic
        find_matches(item)
        
        flash('Item posted successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('post_item.html', title='Post Item', form=form)

@app.route("/hod_dashboard")
@login_required
def hod_dashboard():
    if current_user.role != 'HOD':
        return redirect(url_for('home'))
    pwd_form = HODPasswordChangeForm()
    all_items = Item.query.filter_by(is_high_value=True).order_by(Item.created_at.desc()).all()
    return render_template('hod_dashboard.html', all_items=all_items, pwd_form=pwd_form)

@app.route("/hod/change_password", methods=['POST'])
@login_required
def hod_change_password():
    if current_user.role != 'HOD':
        return redirect(url_for('home'))
    form = HODPasswordChangeForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password, form.old_password.data):
            current_user.password = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Password changed successfully!', 'success')
        else:
            flash('Incorrect current password.', 'danger')
    else:
        for err in form.errors.values():
            flash(f"Error: {err[0]}", 'danger')
    return redirect(url_for('hod_dashboard'))

@app.route("/dashboard")
@login_required
def dashboard():
    user_items = Item.query.filter_by(user_id=current_user.id).order_by(Item.created_at.desc()).all()
    # Matches would be queried here similarly to Django
    return render_template('dashboard.html', items=user_items)

@app.route("/item/<int:item_id>")
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    
    # Logic for Claim Flow: Check if current user has a matching LOST item
    matching_lost_items = []
    if current_user.is_authenticated and item.type == 'FOUND' and item.status == 'OPEN':
        matching_lost_items = Item.query.filter_by(
            user_id=current_user.id, 
            type='LOST', 
            status='OPEN', 
            category_id=item.category_id
        ).all()
        
    return render_template('item_detail.html', item=item, matching_lost_items=matching_lost_items)

@app.route("/search")
def search():
    query = request.args.get('q')
    items = Item.query.filter(
        (Item.title.contains(query)) | 
        (Item.description.contains(query)) |
        (Item.location.contains(query))
    ).all() if query else []
    categories = Category.query.all()
    return render_template('home.html', items=items, categories=categories, title="Search Results")

@app.route("/report/<int:item_id>", methods=['GET', 'POST'])
@login_required
def report_item(item_id):
    item = Item.query.get_or_404(item_id)
    form = ReportForm()
    if form.validate_on_submit():
        report = Report(reason=form.reason.data, item_id=item.id, reporter_id=current_user.id)
        db.session.add(report)
        db.session.commit()
        flash('Report submitted for review', 'success')
        return redirect(url_for('item_detail', item_id=item.id))
    return render_template('report_item.html', title='Report Item', form=form, item=item)

@app.route("/integrity")
def integrity():
    resolved_items = Item.query.filter_by(status='CLAIMED').order_by(Item.id.desc()).all()
    reports = Report.query.order_by(Report.id.desc()).all()
    return render_template('integrity.html', title="Network Integrity", resolved_items=resolved_items, reports=reports)

@app.route("/claim/<int:item_id>", methods=['GET', 'POST'])
@login_required
def claim_item(item_id):
    """Claim a FOUND item by providing the matching LOST item's verification code."""
    found_item = Item.query.get_or_404(item_id)
    # Ensure only the Finder (who posted the item) can verify the claim
    if found_item.user_id != current_user.id:
        flash('Only the person who posted this item can verify a claim.', 'danger')
        return redirect(url_for('item_detail', item_id=item_id))

    if found_item.type != 'FOUND' or found_item.status != 'OPEN':
        flash('This item cannot be claimed.', 'warning')
        return redirect(url_for('item_detail', item_id=item_id))
    
    form = ClaimForm()
    if form.validate_on_submit():
        code = form.verification_code.data.strip().upper()
        lost_item = Item.query.filter_by(verification_code=code, type='LOST', status='OPEN').first()
        if lost_item and lost_item.category_id == found_item.category_id:
            lost_item.status = 'CLAIMED'
            found_item.status = 'CLAIMED'
            db.session.commit()
            flash('Verification successful! Use this code to confirm the return of the item.', 'success')
            return redirect(url_for('item_detail', item_id=item_id))
        else:
            flash('Invalid verification code. Please check the code provided by the claimant.', 'danger')
    return render_template('claim_item.html', title='Claim Item', form=form, item=found_item)

# --- DATABASE INITIALIZATION (Run on Import) ---
with app.app_context():
    db.create_all()
    # Force column alter for Render PostgreSQL to fix login truncation bug
    try:
        if db.engine.name == 'postgresql':
            db.session.execute(db.text('ALTER TABLE "user" ALTER COLUMN password TYPE VARCHAR(255);'))
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Migration error: {e}")

    # Create default categories if they don't exist
    if not Category.query.first():
        db.session.add(Category(name='Electronics'))
        db.session.add(Category(name='Clothing'))
        db.session.add(Category(name='Keys'))
        db.session.add(Category(name='Wallets/Purses'))
        db.session.add(Category(name='ID Cards'))
        db.session.commit()

# --- APP START ---
if __name__ == '__main__':
    app.run(debug=True)