from flask import Flask, render_template, redirect, request, flash, session
from mysqlconnection import MySQLConnector
import re
import md5
from datetime import datetime
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
mysql = MySQLConnector(app,'regestration')
app.secret_key = 'KeepItSecretKeepItSafe'
@app.route('/')
def main():
    return render_template('index.html')
@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    first = request.form['first']
    last = request.form['last']
    password = md5.new(request.form['password']).hexdigest();
    confirm = md5.new(request.form['confirm']).hexdigest();
    count = 0
    query = "INSERT INTO users (first_name, last_name, email, password) VALUES(:first, :last, :email, :password)"
    data= {
    'first': request.form['first'],
    'last': request.form['last'],
    'email': request.form['email'],
    'password': md5.new(request.form['password']).hexdigest()
    }
    mysql.query_db(query, data)
    if len(email) < 1:
        flash("email cannot be empty", 'error')
    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!", 'error')
        count += 1
    if len(first)< 2:
        flash("first name cannot be empty", 'error')
        count += 1
    elif first.isalpha()  == False:
        flash('name feilds cannot contain numbers', 'error')
        count += 1
    if len(last) < 2:
        flash("last name cannot be empty", 'error')
        count += 1
    elif last.isalpha()  == False:
        flash('name feilds cannot contain numbers', 'error')
        count += 1
    if len(password) < 8:
        flash('password must be at least 8 characters long', 'error')
        count += 1
    elif password.isalpha() == True:
        flash('password must have at least one number', 'error')
        count += 1
    elif password.islower() == True:
        flash("password must have one upper case character")
        count += 1
    elif password != confirm:
        flash('password and password confirmation must match', 'error')
        count += 1
    if count == 0:
        return redirect ('/wall')
    else:
        return redirect ('/')
@app.route('/login', methods=['POST'])
def login():
    count = 0

    email = request.form['emails']
    # password = md5.new(request.form['passwords']).hexdigest()
    password = request.form['passwords']
    query = 'SELECT * FROM users WHERE email = :email and password = :password'
    data = {
    'email': email,
    'password': password
    }
    reg = mysql.query_db(query, data)
    session['id'] = reg[0]['id']
    if len(email) < 1:
        flash("email cannot be empty", 'error')
    elif not EMAIL_REGEX.match(request.form['emails']):
        flash("Invalid Email Address!", 'error')
        count += 1
    if len(password) < 8:
        flash('password must be at least 8 characters long', 'error')
        count += 1
    elif password.isalpha() == True:
        flash('password must have at least one number', 'error')
        count += 1
    elif password.islower() == True:
        flash("password must have one upper case character")
        count += 1
    if len(reg) <1:
        flash('please register', 'error')
        return redirect('/')
    else:
        return redirect ('/wall')
    if count == 0:
        return redirect ('/wall')
    else:
        return redirect('/')
@app.route('/wall')
def wall():
    return render_template ('wall.html')
@app.route('/post', methods=['POST'])
def post():
    query = 'INSERT INTO messages (message, users_id, created_at, updated_at) VALUES (:a_message, :users_id, NOW(), NOW())'
    data = {
    'a_message': request.form['message'],
    'users_id': session['id']
    }
    mysql.query_db(query, data)
    myquery = 'SELECT messages.message, messages.id, CONCAT_WS(" ", users.first_name, users.last_name) as name FROM messages JOIN users ON users.id = messages.users_id'
    session['content'] = mysql.query_db(myquery)


    query2 = 'INSERT INTO comments (comment, users_id, created_at, updated_at, messages_id) VALUES (:a_comment, :users_id, NOW(), NOW(), :messages_id)'
    commentdata = {
    'a_comment': request.form['comment'],
    'users_id': session['id'],
    'messages_id': request.form['ids']
    }
    session['content'] = mysql.query_db(query2, commentdata)
    commentquery = 'SELECT comments.comment, CONCAT_WS(" ", users.first_name, users.last_name) as name FROM comments JOIN users ON users.id = comments.users_id JOIN messages ON messages.id = comments.messages_id'
    session['comment'] = mysql.query_db(commentquery)
    return redirect ('/wall')
app.run(debug=True)
