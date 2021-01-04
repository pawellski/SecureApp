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
            self.sql.execute(f"INSERT INTO user (login, password, name, surname, email) VALUES ('{login}', '{password}', '{name}', '{surname}', '{email}')")
            self.db.commit()
            self.sql.execute("SELECT login, password FROM user;")
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def user_exists(self, login):
        try:
            self.sql.execute(f"SELECT EXISTS (SELECT login FROM user WHERE login = '{login}')")
            exists, = self.sql.fetchone()
            return exists
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def get_user_password(self, login):
        try:
            self.sql.execute(f"SELECT password FROM user WHERE login = '{login}'")
            password, = self.sql.fetchone() or (None,)
            return password
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")
    
    def get_host_attempt(self, ip):
        try:
            self.sql.execute(f"SELECT attempt FROM host WHERE ip = '{ip}'")
            attempt, = self.sql.fetchone()
            return attempt
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def set_host_attempt(self, ip, attempt):
        try:
            self.sql.execute(f"UPDATE host SET attempt = {attempt} WHERE  ip = '{ip}'")
            self.db.commit()
            self.sql.execute("SELECT ip, attempt, expire_block FROM host;")
            print("SET HOST ATTEMPT")
            for x, y, z, in self.sql:
                print(x)
                print(y)
                print(z)
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def set_host_block(self, ip):
        try:
            self.sql.execute(f"UPDATE host SET attempt = 5, expire_block = (SELECT NOW() + INTERVAL 1 MINUTE) WHERE  ip = '{ip}'")
            self.db.commit()
            self.sql.execute("SELECT ip, attempt, expire_block FROM host;")
            print("SET HOST BLOCK")
            for x, y, z, in self.sql:
                print(x)
                print(y)
                print(z)
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def block_exists(self, ip):
        try:
            self.sql.execute(f"SELECT EXISTS (SELECT ip FROM host WHERE ip = '{ip}')")
            ip_exists, = self.sql.fetchone()
            print(ip_exists)
            if ip_exists == 0:
                self.sql.execute(f"INSERT INTO host (ip, attempt, expire_block) VALUES ('{ip}', 0, null)")
                self.db.commit()
                print("JEST JUZ NOWY REKORD")
                return 0
            self.sql.execute(f"SELECT expire_block FROM host WHERE ip = '{ip}'")
            expire_block, = self.sql.fetchone() or (None,)
            print(expire_block)
            if expire_block is not None:
                print("IS NOT NULL EB")
                self.sql.execute(f"SELECT CASE WHEN (SELECT NOW()) < (SELECT expire_block FROM host WHERE ip = '{ip}') THEN 1 ELSE 0 END")
                exists, = self.sql.fetchone()
                print(exists)
                if exists == 0:
                    self.sql.execute(f"UPDATE host SET attempt = 0, expire_block = null WHERE  ip = '{ip}'")
            else:
                exists = 0

            self.sql.execute("SELECT ip, attempt, expire_block FROM host;")
            print("BLOCK EXISTS")
            for x, y, z, in self.sql:
                print(x)
                print(y)
                print(z)
            return exists
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def clear_host(self, ip):
        try:
            self.sql.execute(f"UPDATE host SET attempt = 0, expire_block = null WHERE  ip = '{ip}'")
            self.db.commit()
            self.sql.execute("SELECT ip, attempt, expire_block FROM host;")
            print("CLEAR HOST")
            for x, y, z, in self.sql:
                print(x)
                print(y)
                print(z)
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def set_login_and_ip(self, login, ip):
        try:
            self.sql.execute(f"INSERT INTO assignment_ip (login, ip) VALUES ('{login}', '{ip}')")
            self.db.commit()
            self.sql.execute("SELECT login, ip FROM assignment_ip;")
            print("SET LOGIN AND IP")
            for x, y, in self.sql:
                print(x)
                print(y)
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def get_login_and_ip(self, login, ip):
        try:
            self.sql.execute(f"SELECT EXISTS (SELECT ip FROM assignment_ip WHERE ip = '{ip}' AND login = '{login}')")
            exists, = self.sql.fetchone()
            print("GET LOGIN AND IP")
            for x, y, in self.sql:
                print(x)
                print(y)
            print(exists)
            return exists
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")

    def get_user_email(self, login):
        try:
            self.sql.execute(f"SELECT email FROM user WHERE login = '{login}'")
            email, = self.sql.fetchone() or (None,)
            return email
        except mariadb.Error as error:
            flask.flash(f"Database error: {error}")