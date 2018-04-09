from flask import Flask, request, redirect, render_template, session, flash
import re
from mysqlconnection import MySQLConnector

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = "secret"
mysql = MySQLConnector(app,'emailValidationdb')

@app.route('/')
def index():
	# query = "SELECT * FROM email"                           
	# email = mysql.query_db(query)    
	return render_template('index.html')

@app.route('/datain', methods=['POST'])
def create():
	query = "SELECT * FROM email"                           
	email = mysql.query_db(query)  

	if not EMAIL_REGEX.match(request.form["email"]):
		print "FALSE"
		flash("Invalid Email!")
		return redirect('/')

	for e in email:
		if e['email'] == request.form['email']:
			flash("Email Exit!")
			return redirect('/')
	
	query = "INSERT INTO email (email, created_at, updated_at) VALUES (:email, NOW(), NOW())"
	data = {
		'email': request.form['email'],

	}
	mysql.query_db(query, data)
	return redirect('/success')
	


@app.route('/success')
def make(): 
	query = "SELECT * FROM email"                           
	email = mysql.query_db(query)
	return render_template('success.html', all_email=email)


app.run(debug=True, port=5008)