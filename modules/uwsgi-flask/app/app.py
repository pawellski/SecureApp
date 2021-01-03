import time
from flask import Flask
from flask import request
from flask import make_response, render_template
from .mariadb_dao import MariaDBDAO
import bcrypt, hashlib, re, os

POST = "POST"
PEPPER = "PEPPER"

app = Flask(__name__)
dao = MariaDBDAO("mariadb")

@app.route('/')
def index():
    return make_response(render_template("index.html"), 200)

@app.route('/signup', methods=[POST])
def signup():
    form = request.form
    errors = signup_validation(form)
    if len(errors) == 0:
        hashed_password = hashlib.sha256((form.get("password") + os.environ.get(PEPPER)).encode('utf-8'))
        hashed_password = hashlib.sha256(hashed_password.hexdigest().encode('utf-8'))
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(hashed_password.hexdigest().encode('utf-8'), salt).decode('utf-8')
        dao.set_new_user(form.get("login"), hashed_password, form.get("name"), form.get("surname"), form.get("email"))
        del salt
        del hashed_password
        return {"registration": "Accept"}, 201
    else:
        errors["registration"] = "Reject"
        return errors, 400

def signup_validation(form):
    errors = {}
    name = form.get("name")
    surname = form.get("surname")
    email = form.get("email")
    login = form.get("login")
    password = form.get("password")

    if name.isalpha() == False:
        errors["name"] = "Name incorrect."
    if surname.isalpha() == False:
        errors["surname"] = "Surname incorrect."
    if surname.isalpha() == False:
        errors["surname"] = "Surname incorrect."
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors["email"] = "Email incorrect."
    if login.isalnum() == False or len(login) < 5:
        errors["login"] = "Login incorrect."
    if dao.user_exists(login) == 1:
        errors["login_exists"] = "Login already exists."
    if password.isspace() or password is None:
        errors["password"] = "Password incorrect."
    return errors
