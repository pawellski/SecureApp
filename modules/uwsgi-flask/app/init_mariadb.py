import mysql.connector as mariadb
import os

PASSWORD = "MYSQL_ROOT_PASSWORD"

db = mariadb.connect(host="mariadb", user="root", password=os.environ.get(PASSWORD))
sql = db.cursor()
sql.execute("DROP DATABASE IF EXISTS db;")
sql.execute("CREATE DATABASE db;")
sql.execute("USE db;")

sql.execute("DROP TABLE IF EXISTS user;")
sql.execute("CREATE TABLE user (login VARCHAR(32), password VARCHAR(128), name VARCHAR(64), surname VARCHAR(64), email VARCHAR(64));")
sql.execute("DELETE FROM user;")
sql.execute("INSERT INTO user (login, password, name, surname, email) VALUES ('user', 'pass', 'User', 'Pass', 'e@mail');")

sql.execute("DROP TABLE IF EXISTS session;")
sql.execute("CREATE TABLE session (sid VARCHAR(32), login VARCHAR(32), PRIMARY KEY(sid));")
sql.execute("DELETE FROM session;")
sql.execute("INSERT INTO session (sid, login) VALUES ('session1', 'user');")

sql.execute("DROP TABLE IF EXISTS posts;")
sql.execute("CREATE TABLE posts (id INT AUTO_INCREMENT, login VARCHAR(32), post VARCHAR(256), PRIMARY KEY(id));")
sql.execute("DELETE FROM posts;")
sql.execute("INSERT INTO posts (login, post, id) VALUES ('user', 'To jest sekret!', 1);")
db.commit()

sql.execute("SELECT login FROM user;")
for u, in sql:
    print(u)

sql.execute("SELECT password FROM user")
print(sql.fetchall())

sql.execute("SELECT password FROM user WHERE login = 'user'")
pw, = sql.fetchone()
print(pw)