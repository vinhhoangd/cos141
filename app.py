from flask import Flask, request, session, redirect, url_for, render_template
from flaskext.mysql import MySQL
import pymysql
import re
import yaml

app = Flask(__name__)
mysql = MySQL()
db = yaml.safe_load(open('db.yaml'))

print(db)

app.config['MYSQL_DATABASE_HOST'] = db['mysql_host']
app.config['MYSQL_DATABASE_USER'] = db['mysql_user']
app.config['MYSQL_DATABASE_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DATABASE_DB'] = db['mysql_db']

mysql.init_app(app)

# change this to your secret key
app.secret_key = "feitian"


# http://localhost:5000/login/ - this will be the login page
@app.route("/login/", methods=["GET", "POST"])
def login():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    msg = ""

    if (request.method == "POST"
        and "username" in request.form
        and "password" in request.form):
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM accounts WHERE username = %s AND password = %s",
            (username, password),
        )
        account = cursor.fetchone()

        if account:
            session["loggedin"] = True
            session["id"] = account["id"]
            session["username"] = account["username"]
            return redirect(url_for("home"))
        else:
            msg = "Incorrect username/password!"

    return render_template("index.html", msg=msg)


# http://localhost:5000/register - this will be the registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    msg = ""

    if (request.method == "POST"
        and "username" in request.form
        and "password" in request.form
        and "email" in request.form):
        fullname = request.form["fullname"]
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        cursor.execute("SELECT * FROM accounts WHERE username = %s", (username))
        account = cursor.fetchone()

        if account:
            msg = "Account already exists!"
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            msg = "Invalid email address!"
        elif not re.match(r"[A-Za-z0-9]+", username):
            msg = "Username must contain only characters and numbers!"
        elif not username or not password or not email:
            msg = "Please fill out the form!"
        else:
            cursor.execute(
                "INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s)",
                (fullname, username, password, email),
            )
            conn.commit()
            msg = "You have successfully registered!"

    elif request.method == "POST":
        msg = "Please fill out the form!"

    return render_template("register.html", msg=msg)


# http://localhost:5000/home - this will be the home page, only accessible for loggedin users
@app.route("/")
def home():
    if "loggedin" in session:
        return render_template("home.html", username=session["username"])

    return redirect(url_for("login"))


# http://localhost:5000/logout - this will be the logout page
@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)

    return redirect(url_for("login"))


# http://localhost:5000/profile - this will be the profile page, only accessible for loggedin users
@app.route("/profile")
def profile():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if "loggedin" in session:
        cursor.execute("SELECT * FROM accounts WHERE id = %s", [session["id"]])
        account = cursor.fetchone()
        return render_template("profile.html", account=account)

    return redirect(url_for("login"))


@app.route("/newsletter", methods=["GET", "POST"])
def newsletter():
    msg = ""
    if request.method == "POST":
        fullname = request.form["fullname"]
        email = request.form["email"]    
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            "INSERT INTO users VALUES (NULL, %s, %s)",
            (fullname, email),
        )
        conn.commit()
        msg = "Successfully inserted into users table."
    else:
        fullname = "Vinh"

    return render_template("newsletter.html", fullname=fullname, msg=msg)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8081)
