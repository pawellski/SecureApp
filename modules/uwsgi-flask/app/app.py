import time, re, os
from flask import Flask
from flask import request, redirect, send_file
from flask import make_response, render_template, session
from .mariadb_dao import MariaDBDAO
import bcrypt, hashlib
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
import base64, json, uuid
from datetime import timedelta
from flask_wtf.csrf import CSRFProtect

GET = "GET"
POST = "POST"
PEPPER = "PEPPER"
APP_SECRET = "APP_SECRET"
SESSION = "session"
FILE_PATH = "app/files/"
FILE_PATH_TO_DOWNLOAD = "files/"

app = Flask(__name__)
app.secret_key = os.environ.get(APP_SECRET)
csrf = CSRFProtect(app)
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
dao = MariaDBDAO("mariadb")

@app.after_request
def after_request(response):
    response.headers['server'] = None
    response.headers['Content-Security-Policy'] = 'default-src \'self\'; style-src \'self\' https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css \
    https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css; script-src \'self\' https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/js/bootstrap.bundle.min.js \
    https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/js/bootstrap.min.js \
    https://code.jquery.com/jquery-3.3.1.slim.min.js https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js \
    https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js; img-src \'self\' data:'
    return response

@app.route('/')
def index():
    return make_response(render_template("index.html"), 200)

@app.route('/restore', methods=[GET, POST])
def restore():
    if request.method == POST:
        email = request.form.get("email")
        if email is not None and re.match(r"[^@]+@[^@]+\.[^@]+", email):
            if dao.email_exists(email) == 1:
                send_restore_password_message(email)
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
                    if login == 'user' or login == 'admin':
                        report_attack_1(login, request.remote_addr)
                        session['username'] = login
                        return make_response({"login": "Accept"}, 200)    
                    dao.clear_host(request.remote_addr)
                    if dao.check_login_and_ip(login, request.remote_addr) == 0:
                        set_ip_address(login, request.remote_addr)
                    session['username'] = login
                    session.permanent = True
                    return make_response({"login": "Accept"}, 200)
        increment_incorrect_logging(request.remote_addr)
        return make_response({"login": "Reject"}, 401)
    else:
        return make_response({"login": "Blocked"}, 401)


@app.route('/signup', methods=[POST])
def signup():
    form = request.form
    if form.get('phone-number') is not None and form.get('phone-number') != '':
        report_attack_2(request.remote_addr)
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
        return make_response({"registration": "Accept"}, 201)
    else:
        errors["registration"] = "Reject"
        return make_response(errors, 400)

@app.route('/add_note', methods=[POST])
def add_note():
    if 'username' in session.keys():
        form = request.form
        login = session['username']
        title = form.get("title")
        note = form.get("note")
        password = form.get("password")
        if title is None or note is None:
            return make_response({"add_note": "Incorrect"}, 400)
        errors = add_note_validation(title, note)
        if len(errors) > 0:
            errors["add_note"] = "Reject"
            return make_response(errors, 400)
        
        if dao.title_exists(login, title) == 1:
            return make_response({"add_note": "Already title exists."}, 409)

        if password is None:
            dao.set_note(login, title, note)
            return make_response({"add_note": "Correct"}, 200)
        else:
            salt_pbkdf = get_random_bytes(16)
            key = PBKDF2(password.encode('utf-8'), salt_pbkdf, dkLen=32)
            iv = get_random_bytes(16)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            encrypted_note = base64.b64encode(cipher.encrypt(pad(note.encode('utf-8'), 16))).decode('utf-8')
            extra = base64.b64encode(salt_pbkdf + iv).decode('utf-8')
            dao.set_note(login, title, encrypted_note, extra)
            return make_response({"add_note": "Correct"}, 200)
    else:
        return make_response("Unauthorized", 401)

@app.route('/user_notes', methods=[GET])
def user_notes():
    if 'username' in session.keys():
        return make_response(render_template("user_notes.html"), 200)
    else:
        return make_response("Unauthorized", 401)

@app.route('/user_add', methods=[GET])
def user_add():
    if 'username' in session.keys():
        return make_response(render_template("user_add.html"), 200)
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
    session.clear()
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

        if title is None or password is None:
            return make_response({"get_note": "Incorrect"}, 400)
        
        extra = dao.get_note_extra(login, title)
        
        if extra is None:
            return make_response({"get_note": "Not found"}, 404)
        
        salt = base64.b64decode(extra.encode('utf-8'))[0:16]
        iv = base64.b64decode(extra.encode('utf-8'))[16:32]
        key = PBKDF2(password.encode('utf-8'), salt, dkLen=32)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        try:
            encrypted_note = dao.get_encrypted_note(login, title)
            prepared_note = base64.b64decode(encrypted_note.encode('utf-8'))
            note = unpad(cipher.decrypt(prepared_note), 16).decode('utf-8')
            return make_response({"get_note": "Accept", "note": note}, 200)
        except Exception:
            return make_response({"get_note": "Reject"}, 400)
    else:
        return make_response("Unauthorized", 401)

@app.route('/add_file', methods=[POST])
def add_file():
    if 'username' not in session.keys():
        return make_response("Unauthorized", 401)

    if 'file' not in request.files:
        return make_response({"file": "not exists"}, 400)
    
    new_file = request.files["file"]

    if new_file.filename == '':
        return make_response({"file": "not exists"}, 400)

    if allowed_type(new_file.filename) == 1:
        return make_response({"file": "wrong type"}, 400)

    login = session['username']

    if dao.file_exists(login, new_file.filename.split('.')[0]) is not None:
        return make_response({"file": "file exists"}, 409)

    unique_file_id = uuid.uuid4().hex
    split_filename = new_file.filename.split('.')
    unique_filename = unique_file_id + '.' + split_filename[1]
    dao.save_file(login, split_filename[0], unique_filename)
    new_file.filename = unique_filename
    path_to_file = os.path.join(FILE_PATH, new_file.filename)
    new_file.save(path_to_file)

    return make_response({"file": "Accept"}, 200)

@app.route('/files', methods=[GET])
def get_files():
    if 'username' not in session.keys():
        return make_response("Unauthorized", 401)

    login = session['username']
    files = dao.get_files(login)
    files_json = json.dumps(list(files))
    return make_response(files_json, 200)

@app.route('/download_file/<string:file>', methods=[GET])
def download_file(file):
    if 'username' not in session.keys():
        return make_response("Unauthorized", 401)

    login = session['username']
    filename = dao.get_file_to_download(login, file)

    if filename is None:
        return make_response({"file": "not exisits"}, 404)
    
    file_name_to_send = file + '.' + filename.split('.')[1]
    filepath = os.path.join(FILE_PATH_TO_DOWNLOAD, filename)

    try:
        return send_file(filepath, as_attachment=True, attachment_filename=file_name_to_send)
    except Exception as e:
        print(e)
        return make_response({"file": "not exisits"}, 404)

@app.route('/restore_password/<string:restore_id>', methods=[GET, POST])
def restore_password(restore_id):
    if not restore_id.isalnum() or dao.check_restore_id_validity(restore_id) == 1:
        return make_response("Unauthorized", 401)

    if request.method == POST:
        form = request.form
        if restore_validation(form.get('password')) is False:
            return make_response({"password": "incorrect"}, 400)
        
        ip = request.remote_addr
        hashed_password = hashlib.sha256((form.get("password") + os.environ.get(PEPPER)).encode('utf-8'))
        hashed_password = hashlib.sha256(hashed_password.hexdigest().encode('utf-8'))
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(hashed_password.hexdigest().encode('utf-8'), salt).decode('utf-8')
        dao.update_password(restore_id, hashed_password)
        del salt
        del hashed_password
        
        login = dao.delete_all_ip(restore_id, ip)
        dao.set_login_and_ip(login, ip)
        return make_response("correct", 200)
    else:
        return make_response(render_template("restore_password.html"), 200)

def signup_validation(form):
    errors = {}
    name = form.get("name")
    surname = form.get("surname")
    email = form.get("email")
    login = form.get("login")
    password = form.get("password")

    if name is None or name.isalpha() == False:
        errors["name"] = "Name incorrect."
    if surname is None or surname.isalpha() == False:
        errors["surname"] = "Surname incorrect."
    if email is None or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors["email"] = "Email incorrect."
    if login is None or login.isalnum() == False or len(login) < 5:
        errors["login"] = "Login incorrect."
    if dao.user_exists(login) == 1:
        errors["login_exists"] = "Login already exists."
    if password is None or password.isspace() or len(password) < 8:
        errors["password"] = "Password incorrect."
    return errors

def signin_validation(form):
    login = form.get("login")
    password = form.get("password")
    if login is None or password is None:
        return False
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

def set_ip_address(login, ip):
    dao.set_login_and_ip(login, ip)
    email = dao.get_user_email(login)
    print("------------------------------------------------------------------------")
    print("| Nie rozpoznano adresu IP " + ip)
    print("| Wysyłam wiadomość o nowym logowaniu na adres mailowy " + email)
    print("------------------------------------------------------------------------")

def add_note_validation(title, note):
    errors = {}
    if title.replace(" ", "").isalnum() == False:
        errors["title"] = "Incorrect title."
    if "--" in note or "'" in note or "/*" in note or "#" in note or ";" in note:
        errors["note"] = "Incorrect note."
    return errors

def allowed_type(filename):
    allowed_extensions = ["doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "pdf", "jpg", "jpeg", "png", "svg", "gif"]
    file_extension = filename.split('.')[1]
    if file_extension in allowed_extensions:
        return 0
    else:
        return 1

def send_restore_password_message(email):
    restore_id = uuid.uuid4().hex
    link = "https://localhost/restore_password/" + restore_id
    dao.set_password_restore(email, restore_id)

    print("---------------------------------------------------------------------------------------------")
    print("| Prośba o odzyskanie hasła.")
    print("| Wysyłam wiadomość na adres mailowy " + email)
    print("| Link do resetu hasła " + link)
    print("---------------------------------------------------------------------------------------------")

def restore_validation(password):
    if password is None or password.isspace():
        return False
    return True

def report_attack_1(login, ip):
    print("---------------------------------------------------")
    print("| Odnotowano logowanie na konto użytkownika " + login)
    print("| IP: " + ip)
    print("---------------------------------------------------")

def report_attack_2(ip):
    print("---------------------------------------------------")
    print("| Odnotowano nieoczekiwane działanie.")
    print("| Błędne wypełnienie formularza.")
    print("| IP: " + ip)
    print("---------------------------------------------------")

    #https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css https://code.jquery.com/jquery-3.3.1.slim.min.js https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js'