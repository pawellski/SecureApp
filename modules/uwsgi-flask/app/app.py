import time, re, os
from flask import Flask
from flask import request, redirect
from flask import make_response, render_template, session
from .mariadb_dao import MariaDBDAO
import bcrypt, hashlib

GET = "GET"
POST = "POST"
PEPPER = "PEPPER"
APP_SECRET = "APP_SECRET"
SESSION = "session"

app = Flask(__name__)
app.secret_key = os.environ.get(APP_SECRET)
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
dao = MariaDBDAO("mariadb")

@app.route('/')
def index():
    return make_response(render_template("index.html"), 200)

@app.route('/restore', methods=[GET, POST])
def restore():
    if request.method == POST:
        email = request.form.get("email")
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            if dao.email_exists(email) == 1:
                print("------------------------------------------------------------------------------")
                print("| Prośba o odzyskanie hasła.                                                 |")
                print("| Wysyłam wiadomość na adres mailowy " + email + " z linkiem do resetu hasła.|")
                print("------------------------------------------------------------------------------")
                return makre_response({"send_message": "Accept"}, 200)
        return make_response({"send_message": "Reject"}, 400)
    else:
        return make_response(render_template("restore.html"), 200)

@app.route('/signin', methods=[POST])
def signin():
    time.sleep(1)
    form = request.form
    login = form.get("login")
    password = form.get("password")
    if dao.block_exists(request.remote_addr) == 0:
        if signin_validation(form):
            password_db = dao.get_user_password(login)
            if password_db is not None:
                hashed_password = hashlib.sha256((password + os.environ.get(PEPPER)).encode('utf-8'))
                hashed_password = hashlib.sha256(hashed_password.hexdigest().encode('utf-8'))
                if bcrypt.checkpw(hashed_password.hexdigest().encode('utf-8'), password_db.encode('utf-8')):
                    del hashed_password
                    del password_db
                    dao.clear_host(request.remote_addr)
                    if dao.get_login_and_ip(login, request.remote_addr) == 0:
                        check_ip_address(login, request.remote_addr)
                    session['username'] = login
                    return make_response({"login": "Accept"}, 200)
        increment_incorrect_logging(request.remote_addr)
        return make_response({"login": "Reject"}, 401)
    else:
        return make_response({"login": "Blocked"}, 401)


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
        dao.set_login_and_ip(form.get("login"), request.remote_addr)
        del salt
        del hashed_password
        return {"registration": "Accept"}, 201
    else:
        errors["registration"] = "Reject"
        return errors, 400

@app.route('/user_notes', methods=[GET])
def user_notes():
    if 'username' in session.keys():
        return make_response(render_template("user_notes.html"), 200)
    else:
        return make_response("Unauthorized", 401)

@app.route('/user_files', methods=[GET])
def user_files():
    if 'username' in session.keys():
        return make_response(render_template("user_files.html"), 200)
    else:
        return make_response("Unauthorized", 401)

@app.route('/logout', methods=[GET])
def logout():
    session.pop('username', None)
    return redirect("/")

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


def signin_validation(form):
    login = form.get("login")
    if login.isalnum() == False:
        return False
    return True

def increment_incorrect_logging(ip):
    attempt = dao.get_host_attempt(ip)
    attempt = attempt + 1
    if attempt == 5:
        dao.set_host_block(ip)
    else:
        dao.set_host_attempt(ip, attempt)

def check_ip_address(login, ip):
    dao.set_login_and_ip(login, ip)
    email = dao.get_user_email(login)
    print("---------------------------------------------------------------------")
    print("| Nie rozpoznano adresu IP.                                         |")
    print("| Wysyłam wiadomość o nowym logowaniu na adres mailowy " + email + "|")
    print("---------------------------------------------------------------------")
