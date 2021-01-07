import time, re, os
from flask import Flask
from flask import request, redirect
from flask import make_response, render_template, session
from .mariadb_dao import MariaDBDAO
import bcrypt, hashlib
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
import base64, json

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
                return make_response({"send_message": "Accept"}, 200)
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

@app.route('/add_note', methods=[POST])
def add_note():
    if 'username' in session.keys():
        form = request.form
        login = session['username']
        title = form.get("title")
        note = form.get("note")
        password = form.get("password")

        errors = add_note_validation(title, note)
        if len(errors) > 0:
            errors["add_note"] = "Reject"
            return make_response(errors, 400)
        
        if dao.title_exists(login, title) == 1:
            return make_response({"add_note": "Already title exists."}, 409)

        if form.get("password") is None:
            dao.set_note(login, title, note)
            return make_response({"add_note": "Correct"}, 200)
        else:
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            salt_pbkdf = get_random_bytes(16)
            key = PBKDF2(password.encode('utf-8'), salt_pbkdf, dkLen=32)
            iv = get_random_bytes(16)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            encrypted_note = base64.b64encode(cipher.encrypt(pad(note.encode('utf-8'), 16))).decode('utf-8')
            extra = base64.b64encode(salt_pbkdf + iv).decode('utf-8')
            dao.set_note(login, title, encrypted_note, hashed_password, extra)
            return make_response({"add_note": "Correct"}, 200)
    else:
        return make_response("Unauthorized", 401)

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

@app.route('/notes', methods=[GET])
def notes():
    if 'username' in session.keys():
        notes = dao.get_notes()
        json_notes = []
        for note in notes:
            json_note = {"login": note[0], "title": note[1], "note": note[2]}
            json_notes.append(json_note)
        json_notes2 = json.dumps(json_notes)
        return make_response(json_notes2, 200)
    else:
        return make_response("Unauthorized", 401)

@app.route('/encrypted_notes', methods=[GET])
def encrypted_notes():
    if 'username' in session.keys():
        login = session['username']
        notes = dao.get_tiltes_encrypted_notes(login)
        json_notes = []
        for note in notes:
            json_note = {"title": note[0]}
            json_notes.append(json_note)
        json_notes2 = json.dumps(json_notes)
        return make_response(json_notes2, 200)
    else:
        return make_response("Unauthorized", 401)

@app.route('/decrypt_note', methods=[POST])
def decrypt_note():
    if 'username' in session.keys():
        form = request.form
        login = session['username']
        title = form.get("title")
        password = form.get("password")
        print(login)
        print(title)
        print(password)
        db_password = dao.get_note_password(login, title)
        extra = dao.get_note_extra(login, title)
        print(db_password)
        print(extra)

        
        if db_password is None or extra is None:
            return make_response({"get_note": "Not found"}, 404)
        
        if bcrypt.checkpw(password.encode('utf-8'), db_password.encode('utf-8')):
            salt = base64.b64decode(extra.encode('utf-8'))[0:16]
            iv = base64.b64decode(extra.encode('utf-8'))[16:32]
            key = PBKDF2(password.encode('utf-8'), salt, dkLen=32)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            encrypted_note = dao.get_encrypted_note(login, title)
            prepared_note = base64.b64decode(encrypted_note.encode('utf-8'))
            note = unpad(cipher.decrypt(prepared_note), 16).decode('utf-8')
            return make_response({"get_note": "Accept", "note": note}, 200)
        else:
            return make_response({"get_note": "Reject"}, 400)

    else:
        return make_response("Unauthorized", 401)

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

def add_note_validation(title, note):
    errors = {}
    if title.replace(" ", "").isalnum() == False:
        errors["title"] = "Incorrect title."
    if "--" in note or "'" in note or "/*" in note or "#" in note or ";" in note:
        errors["note"] = "Incorrect note."
    return errors