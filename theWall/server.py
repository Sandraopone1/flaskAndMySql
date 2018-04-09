from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import MySQLConnector
import re
import bcrypt

app = Flask(__name__)
app.secret_key = "secret!"
mysql = MySQLConnector(app, "TheWall")

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.-_+]+@[a-zA-Z0-9.-_+]+\.[a-zA-Z]+$')

@app.route("/")
def index():
  
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():

    valid = True

    if len(request.form["first_name"]) < 1:
        flash("First name is required")
        valid = False
    elif len(request.form["first_name"]) < 2:
        flash("first name must be 2 or more characters")
        valid = False

    if len(request.form["last_name"]) < 1:
        flash("Last name is required")
        valid = False
    elif len(request.form["last_name"]) < 2:
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

    if len(request.form["passconf"]) < 1:
        flash("Confirm Password is required")
        valid = False
    elif request.form["passconf"] != request.form["password"]:
        flash("Confirm Password must match Password")
        valid = False

    if valid:
       
        data = {
            "first_name": request.form["first_name"],
            "last_name": request.form["last_name"],
            "email": request.form["email"],
            "password": bcrypt.hashpw(request.form["password"].encode(), bcrypt.gensalt())
        }

        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW());"
        user_id = mysql.query_db(query, data)
        session["username"] = "{} {}".format(request.form["first_name"], request.form["last_name"])
        session["user_id"] = user_id
        if user_id:
        	flash('Registration was successful! Please sign-in to continue.',"success")

        	return redirect("/thewall")

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
        flash('Login successful!')
        return redirect("/thewall")

    else:
        
        flash("Incorrect password")
        return redirect("/")
@app.route("/logout")
def logout():
	session.clear()
	return redirect('/')

@app.route("/thewall")
def thewall():
    if "user_id" not in session:
        flash("You must be signed in to do that!")
        return redirect("/")
    users = mysql.query_db('SELECT * FROM users WHERE id = :id', {'id':session['user_id']})
    user = users[0]
    if not len(users):
		flash("Something went wrong", 'error')
		return redirect('/')

    messagequery = """SELECT messages.id AS messageid, CONCAT(users.first_name, users.last_name) AS user_name, messages.message, DATE_FORMAT(messages.created_at, "%m-%d-%Y") AS created_on 
	FROM users
	JOIN messages ON messages.users_id = users.id
	ORDER BY messages.created_at desc"""
    messagesPosted = mysql.query_db(messagequery)

    commentquery = """SELECT CONCAT(users.first_name, users.last_name) AS username, comments.messages_id, comments.comment, comments.creatted_at
	FROM users
	JOIN comments ON users.id = comments.users_id
	ORDER BY comments.creatted_at desc"""
    CommentsPosted = mysql.query_db(commentquery)
    print CommentsPosted

    return render_template("thewall.html", users = user, wallposts = messagesPosted, commentposts = CommentsPosted)

@app.route("/messages", methods = ["POST"])
def postmessage():

	query = """INSERT INTO messages (messages.users_id, messages.message, messages.created_at, messages.updated_at)
	 VALUES(:user_id, :message, NOW(), NOW() )"""

	data = {
	"user_id":session['user_id'],
	"message": request.form['message']
	}

	messagepost = mysql.query_db(query,data)

	if messagepost:
		flash('Message successfully posted')
		return redirect('/thewall')
	else:
		
		flash('Message post unsuccessful')

@app.route("/comments/<messageid>", methods = ["POST"])
def comments(messageid):
	query = """INSERT INTO comments (comments.messages_id, comments.users_id, comments.comment, comments.creatted_at, comments.updated_at)
	 VALUES(:messageid, :user_id, :comment, NOW(), NOW() )"""
	data ={
	"messageid": messageid,
	"user_id" : session['user_id'],
	"comment": request.form['comment']
	}

	postedcomment = mysql.query_db(query,data)

	if postedcomment:
		flash('Comment posted successfully')
		return redirect('/thewall')
	else:
		
		flash('comment post was unsuccessful')
app.run(debug=True)



# password check
# else:
# 		if len(form['password']) < 8:
# 			errors.append("Password must be at least 8 characters.")
# 		if not any([letter.isupper() for letter in form['password']]):
# 			errors.append("Password must contain at least one uppercase letter.")
# 		if not any([letter.isdigit() for letter in form['password']]):
# 			errors.append("Password must contain at least one number.")
# 		if not any([letter in "!@#$%^&*()-_=+~`\"'<>,.?/:;\}{][|" for letter in form['password']]):
# 			errors.append("Password must contain at least one special character.")
# 		if form['password'] != form['passconf']:
# 			errors.append('Password and confirmation fields must match.')
