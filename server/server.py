from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required
from db_models import db, User
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "users.db")

os.makedirs(DB_DIR, exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DB_PATH

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login" # type: ignore[attr-defined]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/order')
def order():
    return render_template('order.html')

@app.route('/fonts/<path:filename>')
def serve_fonts(filename):
    return send_from_directory('fonts', filename)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(
            username=request.form["username"]
        ).first()

        if user and user.check_password(request.form["password"]):
            login_user(user)
            return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            return "Username already exists", 400

        user = User()
        user.username = username
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/clear_database")
def clear_database():
    db.session.query(User).delete()
    db.session.commit()
    return "Database cleared"

if __name__ == '__main__':
    app.run(debug=True)