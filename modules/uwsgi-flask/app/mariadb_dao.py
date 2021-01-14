import time
import flask
import mysql.connector as mariadb
import os

PASSWORD = "MYSQL_ROOT_PASSWORD"

class MariaDBDAO:

    def connect(self, host, user, password):
        try:
            db = mariadb.connect(host=host, user=user, password=password)
            sql = db.cursor(buffered=True)
            sql.execute("USE mysql")
            sql.execute("SELECT 1")
            sql.fetchall()
            return db
        except Exception as err:
            print(f"Error while connecting with MariaDB: {err}")
            time.sleep(3)
            return None
    
    def choose_database(self, database):
        try:
            sql = self.db.cursor(buffered=True)
            sql.execute(f"USE {database}")
            sql.execute("SELECT 1")
            sql.fetchall()
            return sql
        except Exception as err:
            print(f"Error while choosing DB with MariaDB: {err}")
            print(f"Initiating database ...")
            import app.init_mariadb
            time.sleep(3)
            return None

    def __init__(self, host):
        self.db = None
        self.sql = None
        while self.db is None:
            self.db = self.connect(host, "root", os.environ.get(PASSWORD))
        while self.sql is None:
            self.sql = self.choose_database("db")
        print("Connected to MariaDB.")

    def set_new_user(self, login, password, name, surname, email):
        try:
            self.sql.execute("INSERT INTO user (login, password, name, surname, email) VALUES (%(login)s, %(password)s, %(name)s, %(surname)s, %(email)s)", 
                {'login': login, 'password': password, 'name': name, 'surname': surname, 'email': email})
            self.db.commit()
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def user_exists(self, login):
        try:
            self.sql.execute("SELECT EXISTS (SELECT login FROM user WHERE login = %(login)s)", {'login': login})
            exists, = self.sql.fetchone()
            return exists
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def get_user_password(self, login):
        try:
            self.sql.execute("SELECT password FROM user WHERE login = %(login)s", {'login': login})
            password, = self.sql.fetchone() or (None,)
            return password
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")
    
    def get_host_attempt(self, ip):
        try:
            self.sql.execute("SELECT attempt FROM host WHERE ip = %(ip)s", {'ip': ip})
            attempt, = self.sql.fetchone()
            return attempt
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def set_host_attempt(self, ip, attempt):
        try:
            self.sql.execute("UPDATE host SET attempt = %(attempt)s WHERE  ip = %(ip)s", {'attempt': attempt, 'ip': ip})
            self.db.commit()
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def set_host_block(self, ip):
        try:
            self.sql.execute("UPDATE host SET attempt = 5, expire_block = (SELECT NOW() + INTERVAL 1 MINUTE) WHERE  ip = %(ip)s", {'ip': ip})
            self.db.commit()
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def block_exists(self, ip):
        try:
            self.sql.execute("SELECT EXISTS (SELECT ip FROM host WHERE ip = %(ip)s)", {'ip': ip})
            ip_exists, = self.sql.fetchone()
            if ip_exists == 0:
                self.sql.execute("INSERT INTO host (ip, attempt, expire_block) VALUES (%(ip)s, 0, null)", {'ip': ip})
                self.db.commit()
                return 0
            self.sql.execute("SELECT expire_block FROM host WHERE ip = %(ip)s", {'ip': ip})
            expire_block, = self.sql.fetchone() or (None,)
            if expire_block is not None:
                self.sql.execute("SELECT CASE WHEN (SELECT NOW()) < (SELECT expire_block FROM host WHERE ip = %(ip)s) THEN 1 ELSE 0 END", {'ip': ip})
                exists, = self.sql.fetchone()
                if exists == 0:
                    self.sql.execute("UPDATE host SET attempt = 0, expire_block = null WHERE  ip = %(ip)s", {'ip': ip})
            else:
                exists = 0
            return exists
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def clear_host(self, ip):
        try:
            self.sql.execute("UPDATE host SET attempt = 0, expire_block = null WHERE  ip = %(ip)s", {'ip': ip})
            self.db.commit()
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def set_login_and_ip(self, login, ip):
        try:
            self.sql.execute("INSERT INTO assignment_ip (login, ip) VALUES (%(login)s, %(ip)s)", {'login': login, 'ip': ip})
            self.db.commit()
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def check_login_and_ip(self, login, ip):
        try:
            self.sql.execute("SELECT EXISTS (SELECT ip FROM assignment_ip WHERE ip = %(ip)s AND login = %(login)s)", {'login': login, 'ip': ip})
            exists, = self.sql.fetchone()
            return exists
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def get_user_email(self, login):
        try:
            self.sql.execute("SELECT email FROM user WHERE login = %(login)s", {'login': login})
            email, = self.sql.fetchone() or (None,)
            return email
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def email_exists(self, email):
        try:
            self.sql.execute("SELECT EXISTS (SELECT email FROM user WHERE email = %(email)s)", {'email': email})
            exists, = self.sql.fetchone()
            return exists
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def title_exists(self, login, title):
        try:
            self.sql.execute("SELECT EXISTS (SELECT title FROM posts WHERE login = %(login)s AND title = %(title)s)", {'login': login, 'title': title})
            exists, = self.sql.fetchone()
            return exists
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")
    
    def set_note(self, login, title, note, extra=None):
        try:
            if extra is None:
                self.sql.execute("INSERT INTO posts (login, title, note, extra) VALUES (%(login)s, %(title)s, %(note)s, null)",
                {'login': login, 'title': title, 'note': note})
            else:
                self.sql.execute("INSERT INTO posts (login, title, note, extra) VALUES (%(login)s, %(title)s, %(note)s, %(extra)s)",
                {'login': login, 'title': title, 'note': note, 'extra': extra})
            self.db.commit()
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def get_notes(self):
        try:
            self.sql.execute("SELECT login, title, note FROM posts WHERE extra IS NULL;")
            notes = self.sql.fetchall()
            if len(notes) == 0:
                return []
            return notes
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def get_tiltes_encrypted_notes(self, login):
        try:
            self.sql.execute("SELECT title FROM posts WHERE login = %(login)s AND extra IS NOT NULL;", {'login': login})
            encrypted_notes = self.sql.fetchall()
            if len(encrypted_notes) == 0:
                return []
            return encrypted_notes
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def get_note_extra(self, login, title):
        try:
            self.sql.execute("SELECT extra FROM posts WHERE login = %(login)s AND title = %(title)s", {'login': login, 'title': title})
            extra, = self.sql.fetchone() or (None,)
            return extra
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def get_encrypted_note(self, login, title):
        try:
            self.sql.execute("SELECT note FROM posts WHERE login = %(login)s AND title = %(title)s", {'login': login, 'title': title})
            note, = self.sql.fetchone() or (None,)
            return note
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def save_file(self, login, filename, file_uuid):
        try:
            self.sql.execute("INSERT INTO files (login, filename, file_uuid) VALUES (%(login)s, %(filename)s, %(file_uuid)s)",
            {'login': login, 'filename': filename, 'file_uuid': file_uuid})
            self.db.commit()
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def file_exists(self, login, filename):
        try:
            self.sql.execute("SELECT filename FROM files WHERE login = %(login)s AND filename = %(filename)s", {'login': login, 'filename': filename})
            filename, = self.sql.fetchone() or (None, )
            return filename
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")


    def get_files(self, login):
        try:
            self.sql.execute("SELECT filename FROM files WHERE login = %(login)s", {'login': login})
            files = self.sql.fetchall()
            if len(files) == 0:
                return []
            return files
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def get_file_to_download(self, login, filename):
        try:
            self.sql.execute("SELECT file_uuid FROM files WHERE login = %(login)s AND filename = %(filename)s", {'login': login, 'filename': filename})
            file_uuid, = self.sql.fetchone() or (None, )
            return file_uuid
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def set_password_restore(self, email, restore_id):
        try:
            self.sql.execute("SELECT EXISTS (SELECT email, restore_id, expire_date FROM restore_password WHERE email = %(email)s)", {'email': email})
            exists, = self.sql.fetchone()
            if exists == 0:
                self.sql.execute("INSERT INTO restore_password (email, restore_id, expire_date) VALUES (%(email)s, %(restore_id)s, (SELECT NOW() + INTERVAL 5 MINUTE))", {'email': email, 'restore_id': restore_id})
            else:
                self.sql.execute("UPDATE restore_password SET restore_id = %(restore_id)s, expire_date = (SELECT NOW() + INTERVAL 1 MINUTE) WHERE  email = %(email)s", {'restore_id': restore_id, 'email': email})
            self.db.commit()
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def check_restore_id_validity(self, restore_id):
        try:
            self.sql.execute("SELECT CASE WHEN (SELECT NOW()) < (SELECT expire_date FROM restore_password WHERE restore_id = %(restore_id)s) THEN 0 ELSE 1 END", {'restore_id': restore_id})
            condition, = self.sql.fetchone()
            return condition
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def update_password(self, restore_id, password):
        try:
            self.sql.execute("SELECT email FROM restore_password WHERE restore_id = %(restore_id)s", {'restore_id': restore_id})
            email, = self.sql.fetchone()
            self.sql.execute("UPDATE user SET password = %(password)s WHERE  email = %(email)s", {'password': password, 'email': email})
            self.db.commit()
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def delete_all_ip(self, restore_id, ip):
        try:
            self.sql.execute("SELECT email FROM restore_password WHERE restore_id = %(restore_id)s", {'restore_id': restore_id})
            email, = self.sql.fetchone()
            self.sql.execute("SELECT login FROM user WHERE email = %(email)s", {'email': email})
            login, = self.sql.fetchone()
            self.sql.execute("DELETE FROM assignment_ip WHERE login = %(login)s", {'login': login})
            self.db.commit()
            return login
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")
