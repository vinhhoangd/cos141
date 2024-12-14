from flask import Flask, request, session, redirect, url_for, render_template
from flaskext.mysql import MySQL
import pymysql
import re
import yaml
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
mysql = MySQL()
db = yaml.safe_load(open('db.yaml'))

print(db)

app.config['MYSQL_DATABASE_HOST'] = db['mysql_host']
app.config['MYSQL_DATABASE_USER'] = db['mysql_user']
app.config['MYSQL_DATABASE_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DATABASE_DB'] = db['mysql_db']

mysql.init_app(app)


app.secret_key = "feitian"


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
            "SELECT * FROM accounts WHERE username = %s", (username)
        )

     
        account = cursor.fetchone()

       
        if account and check_password_hash(account["password"], password):
            
            session["loggedin"] = True
            session["id"] = account["id"]
            session["username"] = account["username"]

           
            return redirect(url_for("home"))

        else:
           
            msg = "Incorrect username/password!"

    return render_template("index.html", msg=msg)



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
            
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO accounts (fullname, username, password, email) VALUES (%s, %s, %s, %s)",
                (fullname, username, hashed_password, email),
            )

            conn.commit()
            msg = "You have successfully registered!"

    elif request.method == "POST":
        
        msg = "Please fill out the form!"

    
    return render_template("register.html", msg=msg)



@app.route("/home")
def home():
    
    if "loggedin" in session:

        return render_template("home.html", username=session["username"])

 
    return redirect(url_for("login"))



@app.route("/logout")
def logout():
  
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)

   
    return redirect(url_for("login"))



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

        msg = "Successfully inserted into users table"
    else:
        fullname = "cong"
    return render_template("newsletter.html", fullname=fullname, msg=msg)


@app.route("/settings", methods=["GET", "POST"])
def settings():

    if "loggedin" in session:
      
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

       
        cursor.execute("SELECT * FROM accounts WHERE id = %s", [session["id"]])
        account = cursor.fetchone()

        msg = ""

        if request.method == "POST":
           
            new_email = request.form.get("email")
            new_password = request.form.get("password")

            
            if new_email and re.match(r"[^@]+@[^@]+\.[^@]+", new_email):
                cursor.execute("UPDATE accounts SET email = %s WHERE id = %s", (new_email, session["id"]))
                conn.commit()
                msg = "Accounts setting updated successfully!"
            
            if new_password:
               
                hashed_password = generate_password_hash(new_password)
                cursor.execute("UPDATE accounts SET password = %s WHERE id = %s", (hashed_password, session["id"]))
                conn.commit()
                msg = "Accounts setting updated successfully!"
            else:
                msg = "Invalid input or no changes made!"

      
        return render_template("settings.html", account=account, msg=msg)

   
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")