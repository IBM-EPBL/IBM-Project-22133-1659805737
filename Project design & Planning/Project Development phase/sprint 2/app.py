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
      stmt = ibm_db.prepare(conn,'SELECT * FROM register WHERE username = ? AND password = ?')
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

#ADDING	DATA


@app.route("/add")
def adding():
  return render_template('add.html')


@app.route('/addexpense',methods=['GET', 'POST']) 
def addexpense():

   date = request.form['date']
   expensename = request.form['expensename'] 
   amount = request.form['amount']
   paymode = request.form['paymode']
   category = request.form['category']
   insert_sql = "(INSERT INTO expenses VALUES (NULL, % s, % s, % s, % s, % s, % s)',(session['id'] ,date, expensename, amount, paymode, category)"
   stmt = ibm_db.prepare( conn , insert_sql) 
   ibm_db.bind_param(stmt, 1, session['id'])
   ibm_db.bind_param(stmt, 2, date)
   ibm_db.bind_param(stmt, 3, expensename)
   ibm_db.bind_param(stmt, 4, amount)
   ibm_db.bind_param(stmt, 5, paymode)
   ibm_db.bind_param(stmt, 6, category) 
   ibm_db.execute(stmt)
   print(date + " " + expensename + " " + amount + " " + paymode + " " + category) 
   return redirect("/display")


#DISPLAY	graph

@app.route("/display") 
def display():
 
 print(session["username"],session['id'])
 stmt = ibm_db.prepare(conn,'SELECT * FROM expenses WHERE userid = % s AND date ORDER BY `expenses`.`date` DESC',(str(session['id'])))
 ibm_db.execute(stmt)
 account = ibm_db.fetch_assoc(stmt)
 return render_template('display.html' , expense = 'expense')


#delete---the--data

@app.route('/delete/<string:id>', methods = ['POST', 'GET' ])
def delete(id):
  stmt = ibm_db.prepare(conn,'DELETE FROM expenses WHERE id = {0}'.format(id))
  ibm_db.execute(stmt)
  print('deleted successfully')
  return redirect("/display")


#UPDATE---DATA

@app.route('/edit/<id>', methods = ['POST', 'GET' ]) 
def edit(id):
  stmt = ibm_db.prepare(conn,'SELECT * FROM expenses WHERE id = %s', (id,))
  row = ibm_db.fetch_tuple()
  print(row[0])
  return render_template('edit.html', expenses = row[0])
@app.route('/update/<id>', methods = ['POST']) 
def update(id):
  if request.method == 'POST' :
   date = request.form['date']
   expensename = request.form['expensename'] 
   amount = request.form['amount']
   paymode = request.form['paymode'] 
   category = request.form['category']
   stmt = ibm_db.prepare(conn,"UPDATE `expenses` SET `date` = % s , `expensename` =% s , `amount` = % s, `paymode` = % s, `category` = % s WHERE `expenses`.`id` = % s ",(date, expensename, amount, str(paymode), str(category),id))
   ibm_db.execute(stmt)
   print('successfully updated') 
   return redirect("/display")


#limit 
@app.route("/limit" ) 
def limit():
  return redirect('/limitn')

@app.route("/limitnum" , methods = ['POST' ]) 
def limitnum():
 if request.method == "POST": 
    number= request.form['number']
    stmt = ibm_db.prepare(conn,'INSERT INTO limits VALUES (NULL, % s, % s) ',(session['id'], number))
    ibm_db.execute(stmt) 
    return redirect('/limitn')


@app.route("/limitn")
def limitn():
  stmt = ibm_db.prepare(conn,'SELECT limitss FROM `limits` ORDER BY `limits`.`id` DESC LIMIT 1')
  x= ibm_db.fetch_assoc() 
  s = x[0]


  return render_template("limit.html" , y= s)


#REPORT

#log-out 
@app.route('/logout') 
def logout():
  session.pop('loggedin', None) 
  session.pop('id', None)
  session.pop('username', None) 
  return render_template('home.html')
 

if  __name__	== " main ": app.run(debug=True)
