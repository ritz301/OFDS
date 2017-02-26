from flask import Flask, render_template, request, redirect, url_for, session
from flaskext.mysql import MySQL
 
mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'OFDS'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
db = mysql.connect()
cursor = db.cursor()
 
@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html', error = None)
    elif request.method == "POST":
        error = None
        username = request.form['username']
        password = request.form['password']
        cursor.execute(("SELECT * from users where username=%s AND password=%s"), (username, password))
        data = cursor.fetchone()
        if data is None:
            error = "Invalid Credentials"
        if error is None:
            session['username'] = username
            session['id'] = list(data)[0]
            return redirect(url_for('home'))
        else:
            return render_template("login.html", error = error)

@app.route("/home", methods=['GET', 'POST'])
def home():
    if(request.method == "GET"):
        if 'username' in session:
            username_session = escape(session['username']).capitalize()
            username_id = escape(session['id'])
            return render_template('home.html', session_user_name=username_session, session_id=username_id)
        else:
            return redirect(url_for('login'))
    elif(request.method == "POST"):
        error = None

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route("/user/register", methods=['GET', 'POST'])
def ureg():
    if request.method == "GET":
        return render_template('user_register.html')
    elif request.method == "POST":
        fname = request.form['fname']
        lname = request.form['lname']
        username = request.form['username']
        pass1 = request.form['pass1']
        pass2 = request.form['pass2']
        if pass1 != pass2:
            return "Passwords do not match"
        else:
            check = ("SELECT * FROM users WHERE username = %s")
            data = (username)
            cursor = db.cursor()
            cursor.execute(check, data)
            if cursor.fetchone() is None:
                cursor1 = db.cursor()
                add_user = ("INSERT INTO users "
                   "(fname, lname, username, password) "
                   "VALUES (%s, %s, %s, %s)")
                data = (fname, lname, username, pass1)
                cursor1.execute(add_user, data)
                db.commit()
                return redirect(url_for('login'))
            else:
                data = {}
                data['to_show'] = True
                data["error"] = "Username already exists"
                return render_template("user_register.html", **data)

@app.route("/restaurant/register", methods=['GET', 'POST'])
def rreg():
    if(request.method == "GET"):
        return render_template('restaurant_register.html')
    elif(request.method == "POST"):
        fname = request.form['fname']
        lname = request.form['lname']
        username = request.form['username']
        pass1 = request.form['pass1']
        pass2 = request.form['pass2']
        if(pass1 != pass2):
            return "Passwords do not match"
        else:
            add_user = ("INSERT INTO users "
               "(fname, lname, username, password) "
               "VALUES (%s, %s, %s, %s, %s)")
            data = (fname, lname, username, password)
            cursor.execute(add_user, data)
            db.commit()
            return render_template('login.html', status='Successfully registered')

app.secret_key = '\x1e.\xef\x1bd\xf6~\'\x16=\xfdy\xbc\xf2\xd2\xffb\xba"\x1fO\x9ez\xff'

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=4000, debug=True)

