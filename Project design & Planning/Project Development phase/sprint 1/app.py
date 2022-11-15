from flask import Flask, redirect, url_for, render_template, request, flash, session 
import ibm_db
import re
app = Flask(__name__) 
app.secret_key = 'a' 
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=21fecfd8-47b7-4937-840d-d791d0218660.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31864;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=gsk43831;PWD=6QVZywD7hzIVKjYy",'','')

#HOME--PAGE
@app.route("/home")
def home():
   return render_template("homepage.html")

@app.route("/") 
def add():
   return render_template("home.html")


#SIGN--UP--OR--REGISTER

@app.route("/signup") 
def signup():
   return render_template("signup.html")


@app.route('/register', methods =['GET', 'POST'])
def register(): 
  msg = ''
  if request.method == 'POST' :
     username = request.form['username']
     email = request.form['email']
     password = request.form['password']
     stmt = ibm_db.prepare(conn,'SELECT * FROM register WHERE username = ?') 
     ibm_db.bind_param(stmt,1,username)
     ibm_db.execute(stmt)
     account = ibm_db.fetch_assoc(stmt) 
     if account:
        msg = 'Account already exists !'
     elif not re.match(r'[^@]+@[^@]+\.[^@]+', email): 
        msg = 'Invalid email address !'
     elif not re.match(r'[A-Za-z0-9]+', username):
        msg = 'name must contain only characters and numbers !'
     else:
        insert_sql = "INSERT INTO register VALUES (?, ?, ?)" 
        stmt = ibm_db.prepare(conn,insert_sql) 
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, email)
        ibm_db.bind_param(stmt, 3, password)
        ibm_db.execute(stmt)
        msg = 'You have successfully registered !' 
        return render_template('signup.html', msg = msg)

#LOGIN--PAGE

@app.route("/signin") 
def signin():
   return render_template("login.html")

@app.route('/login',methods =['GET', 'POST']) 
def login():
   global userid 
   msg = ''

   if request.method == 'POST' : 
    username = request.form['username']
    password = request.form['password']
    stmt = ibm_db.prepare(conn,'SELECT * FROM register WHERE username = ?AND password = ?')
    ibm_db.bind_param(stmt,1,username)
    ibm_db.bind_param(stmt,2,password) 
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    print (account)
    if account:
         session['loggedin'] = True
         session['username'] = account['USERNAME'] 
         session['password'] = account['PASSWORD'] 
         msg = 'Logged in successfully !'
         return redirect('/home') 
    else:
         msg = 'Incorrect username / password !' 
    return render_template('login.html', msg = msg)

if  __name__    == "    main    ": 
    app.run(debug=True)
