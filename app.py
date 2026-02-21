from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "supersecurekey123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# =========================
# ROLE DECORATOR
# =========================
def role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            if 'role' not in session:
                return redirect(url_for('login'))

            if session['role'] not in allowed_roles:
                flash("You are not authorized to perform this action!", "error")

                if session['role'] in ['admin', 'manager']:
                    return redirect(url_for('panel'))
                else:
                    return redirect(url_for('dashboard'))

            return func(*args, **kwargs)

        return wrapper
    return decorator


# =========================
# HOME
# =========================
@app.route('/')
def home():
    return redirect(url_for('login'))


# =========================
# REGISTER
# =========================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "error")
            return redirect(url_for('register'))

        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful!", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


# =========================
# LOGIN
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()

        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            session['role'] = user.role

            # Admin + Manager → Same Panel
            if user.role in ['admin', 'manager']:
                return redirect(url_for('panel'))
            else:
                return redirect(url_for('dashboard'))

        flash("Invalid Credentials!", "error")

    return render_template('login.html')


# =========================
# SHARED PANEL (ADMIN + MANAGER)
# =========================
@app.route('/panel')
@role_required(['admin', 'manager'])
def panel():

    users = User.query.all()

    admin_count = User.query.filter_by(role='admin').count()
    manager_count = User.query.filter_by(role='manager').count()
    user_count = User.query.filter_by(role='user').count()

    return render_template(
        'panel.html',
        users=users,
        admin_count=admin_count,
        manager_count=manager_count,
        user_count=user_count
    )


# =========================
# USER DASHBOARD
# =========================
@app.route('/dashboard')
@role_required(['user'])
def dashboard():
    return render_template('dashboard.html')


# =========================
# DELETE USER (ADMIN ONLY)
# =========================
@app.route('/delete/<int:user_id>', methods=['POST'])
@role_required(['admin'])
def delete_user(user_id):

    # 🚨 Prevent admin from deleting himself
    if session['user_id'] == user_id:
        flash("You can't delete your own account!", "error")
        return redirect(url_for('panel'))

    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    flash("User deleted successfully!", "success")
    return redirect(url_for('panel'))


# =========================
# UPDATE ROLE (ADMIN ONLY)
# =========================
@app.route('/update_role/<int:user_id>', methods=['POST'])
@role_required(['admin'])
def update_role(user_id):

    # 🚨 Prevent admin from modifying his own role
    if session['user_id'] == user_id:
        flash("You can't modify your own priority!", "error")
        return redirect(url_for('panel'))

    user = User.query.get_or_404(user_id)
    user.role = request.form['role']

    db.session.commit()

    flash("Role updated successfully!", "success")
    return redirect(url_for('panel'))


# =========================
# LOGOUT
# =========================
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)