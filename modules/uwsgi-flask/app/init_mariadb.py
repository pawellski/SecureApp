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
sql.execute("INSERT INTO user (login, password, name, surname, email) VALUES ('user', '$2b$12$ZGiEDDzPI2cuLetua7Ti3eWoLJ8QgEg61H1FsD5.xA8jD8j9CJViG', 'User', 'Pass', 'user@mail.com');")
sql.execute("INSERT INTO user (login, password, name, surname, email) VALUES ('admin', '$2b$12$.jjpiyASwwaN3lHQBmstne1HVrR8.qET8KVpDTilVAkcG6rXq0wAq', 'Admin', 'Admin', 'admin@admin.com');")

sql.execute("DROP TABLE IF EXISTS host;")
sql.execute("CREATE TABLE host (ip VARCHAR(32), attempt INT, expire_block DATETIME);")
sql.execute("DELETE FROM host;")

sql.execute("DROP TABLE IF EXISTS assignment_ip;")
sql.execute("CREATE TABLE assignment_ip (login VARCHAR(32), ip VARCHAR(32));")
sql.execute("DELETE FROM assignment_ip;")

sql.execute("DROP TABLE IF EXISTS posts;")
sql.execute("CREATE TABLE posts (id INT AUTO_INCREMENT, login VARCHAR(32), title VARCHAR(64), note VARCHAR(1024), extra VARCHAR(128), PRIMARY KEY(id));")
sql.execute("DELETE FROM posts;")

sql.execute("DROP TABLE IF EXISTS files;")
sql.execute("CREATE TABLE files (id INT AUTO_INCREMENT, login VARCHAR(32), filename VARCHAR(128), file_uuid VARCHAR(128), PRIMARY KEY(id));")
sql.execute("DELETE FROM files;")

sql.execute("DROP TABLE IF EXISTS restore_password;")
sql.execute("CREATE TABLE restore_password (email VARCHAR(32), restore_id VARCHAR(128), expire_date DATETIME);")
sql.execute("DELETE FROM restore_password;")

db.commit()