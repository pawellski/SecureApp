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