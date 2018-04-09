from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import MySQLConnector
import re
import bcrypt

app = Flask(__name__)
app.secret_key = "secret!"
mysql = MySQLConnector(app, "login")

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.-_+]+@[a-zA-Z0-9.-_+]+\.[a-zA-Z]+$')

@app.route("/")
def index():
  
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():

    valid = True

    if len(request.form["first"]) < 1:
        flash("First name is required")
        valid = False
    elif len(request.form["first"]) < 2:
        flash("First name must be 2 or more characters")
        valid = False

    if len(request.form["last"]) < 1:
        flash("Last name is required")
        valid = False
    elif len(request.form["last"]) < 2:
        flash("Last name must be 2 or more characters")
        valid = False

    if len(request.form["email"]) < 1:
        flash("Email is required")
        valid = False
    elif not EMAIL_REGEX.match(request.form["email"]):
        flash("Invalid email")
        valid = False
    else:
        matching_emails = mysql.query_db("SELECT * FROM users WHERE email = :email", request.form)
        if len(matching_emails) > 0:
            flash("Email already exists")
            valid = False

    if len(request.form["password"]) < 1:
        flash("Password is required")
        valid = False
    elif len(request.form["password"]) < 8:
        flash("Password must be 8 characters or more")
        valid = False

    if len(request.form["confirm"]) < 1:
        flash("Confirm Password is required")
        valid = False
    elif request.form["confirm"] != request.form["password"]:
        flash("Confirm Password must match Password")
        valid = False

    if valid:
       
        data = {
            "first": request.form["first"],
            "last": request.form["last"],
            "email": request.form["email"],
            "password": bcrypt.hashpw(request.form["password"].encode(), bcrypt.gensalt())
        }

        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first, :last, :email, :password, NOW(), NOW());"
        user_id = mysql.query_db(query, data)
        session["username"] = "{} {}".format(request.form["first"], request.form["last"])
        session["user_id"] = user_id
        return redirect("/the_wall")

    else:
        return redirect("/")

@app.route("/login", methods=["POST"])
def login():

    valid = True

    if len(request.form["email"]) < 1:
        flash("Email is required")
        valid = False
    elif not EMAIL_REGEX.match(request.form["email"]):
        flash("Invalid email")
        valid = False
    else:
        users_with_matching_email = mysql.query_db("SELECT * FROM users WHERE email = :email", request.form)
        if len(users_with_matching_email) < 1:
            flash("Email doesn't exist")
            valid = False

    if len(request.form["password"]) < 1:
        flash("Password is required")
        valid = False
    elif len(request.form["password"]) < 8:
        flash("Password must be 8 characters or more")
        valid = False

    if not valid:
        return redirect("/")

    user = users_with_matching_email[0]

    print user 

    if bcrypt.checkpw(request.form["password"].encode(), user["password"].encode()):
        session["user_id"] = user["id"]
        session["username"] = "{} {}".format(user["first_name"], user["last_name"])
        return redirect("/the_wall")

    else:
        
        flash("Incorrect password")
        return redirect("/")
        
@app.route("/the_wall")
def the_wall():
    if "user_id" not in session:
        return redirect("/")
    return render_template("the_wall.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

app.run(debug=True)
