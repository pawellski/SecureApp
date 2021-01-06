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

sql.execute("DROP TABLE IF EXISTS host;")
sql.execute("CREATE TABLE host (ip VARCHAR(32), attempt INT, expire_block DATETIME);")
sql.execute("DELETE FROM host;")

sql.execute("DROP TABLE IF EXISTS assignment_ip;")
sql.execute("CREATE TABLE assignment_ip (login VARCHAR(32), ip VARCHAR(32));")
sql.execute("DELETE FROM assignment_ip;")

sql.execute("DROP TABLE IF EXISTS posts;")
sql.execute("CREATE TABLE posts (id INT AUTO_INCREMENT, login VARCHAR(32), title VARCHAR(64), note VARCHAR(1024), password VARCHAR(128), extra VARCHAR(128), PRIMARY KEY(id));")
sql.execute("DELETE FROM posts;")
sql.execute("INSERT INTO posts (id, login, title, note, password, extra) VALUES (1, 'user', 'Sekret', 'To jest sekret!', null, null);")
db.commit()

sql.execute("SELECT login FROM user;")
for u, in sql:
    print(u)

sql.execute("SELECT password FROM user")
print(sql.fetchall())

sql.execute("SELECT password FROM user WHERE login = 'user'")
pw, = sql.fetchone()
print(pw)