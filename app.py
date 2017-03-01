from flask import Flask, render_template, request, redirect, url_for, session, escape, Response
from flaskext.mysql import MySQL
import json
 
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
            session['fname'] = list(data)[1]
            return redirect(url_for('home'))
        else:
            return render_template("login.html", error = error)

@app.route("/home", methods=['GET', 'POST'])
def home():
    if(request.method == "GET"):
        if 'username' in session:
            username_session = escape(session['username']).capitalize()
            username_id = escape(session['id'])
            fname = escape(session['fname'])
            return render_template('home.html', fname=fname, username=username_session, userid=username_id)
        else:
            return redirect(url_for('login'))
    elif(request.method == "POST"):
        error = None

@app.route("/cuisines", methods=['GET'])
def cuisines():
    if(request.method == "GET"):
        if 'username' in session:
            cursor.execute("SELECT * from categories")
            data = cursor.fetchall()
            return Response(json.dumps(dict(data)), mimetype='application/json')
        else:
            return redirect(url_for('login'))

@app.route("/cuisines/<cid>", methods=['GET'])
def getRes(cid):
    if(request.method == "GET"):
        if 'username' in session:
            cursor.execute(("SELECT username from search WHERE cuisine_id = %s"), (cid))
            data = cursor.fetchall()
            data2 = []
            for username in data:
                cursor.execute(("SELECT username, name from restaurants WHERE username = %s"), (username))
                temp = cursor.fetchone()
                if temp is not None:
                    data2.append(temp)
            return Response(json.dumps(dict(data2)), mimetype='application/json')
        else:
            return redirect(url_for('login'))

@app.route("/home/cuisines/<id>", methods=['GET'])
def restaurants(id):
    if(request.method == "GET"):
        if 'username' in session:
            username_session = escape(session['username']).capitalize()
            username_id = escape(session['id'])
            fname = escape(session['fname'])
            cursor.execute(("SELECT cname from categories where cuisine_id=%s"), (id))
            data = cursor.fetchone()
            return render_template("restaurants.html", cuisine_id = id, cuisine_name=list(data)[0], fname=fname, username=username_session, userid=username_id)
        else:
            return redirect(url_for('login'))

@app.route("/cuisines/<cid>/<rid>", methods=['GET'])
def getMenu(cid, rid):
    if(request.method == "GET"):
        if 'username' in session:
            cursor.execute(("SELECT * from menu WHERE username = %s"), (rid))
            data = cursor.fetchall()
            return Response(json.dumps(data), mimetype='application/json')
        else:
            return redirect(url_for('login'))

@app.route("/home/cuisines/<cid>/<username>", methods=['GET'])
def menu(cid, username):
    if(request.method == "GET"):
        if 'username' in session:
            username_session = escape(session['username']).capitalize()
            username_id = escape(session['id'])
            fname = escape(session['fname'])
            cursor.execute(("SELECT cname from categories where cuisine_id=%s"), (cid))
            data = cursor.fetchone()
            cursor1 = db.cursor()
            cursor1.execute(("SELECT name from restaurants WHERE username=%s"), (username))
            data1 = cursor1.fetchone()
            if data is None or data1 is None:
                return "Record doesn't exists in table"
            else:
                return render_template("menu.html", res_uname= username, res_name=list(data1)[0], cuisine_id = cid, cuisine_name=list(data)[0], fname=fname, username=username_session, userid=username_id)
        else:
            return redirect(url_for('login'))
        
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
                data["error"] = "Username already exists"
                return render_template("user_register.html", **data)

@app.route("/restaurant/register", methods=['GET', 'POST'])
def rreg():
    if(request.method == "GET"):
        return render_template('restaurant_register.html')
    elif(request.method == "POST"):
        rname = request.form['rname']
        raddress = request.form['raddress']
        username = request.form['username']
        pass1 = request.form['pass1']
        pass2 = request.form['pass2']
        categories = request.form.getlist('category')
        data = {}
        if(pass1 != pass2):
            data["error"] = "Passwords do not match."
            return render_template("restaurant_register.html", **data)
        elif not categories:
            data["error"] = "Please select atleast one category."
            return render_template("restaurant_register.html", **data)
        else:
            check = ("SELECT * FROM restaurants WHERE username = %s")
            data = (username)
            cursor = db.cursor()
            cursor.execute(check, data)
            if cursor.fetchone() is None:
                cursor1 = db.cursor()
                for cat in categories:
                    add_search = ("INSERT INTO search "
                        "(cuisine_id,username) "
                        "VALUES (%s,%s)")
                    val = (int(cat),username)
                    cursor1.execute(add_search,val)
                    db.commit()
                add_restaurant = ("INSERT INTO restaurants "
                    "(name, address, username, password) "
                    "VALUES (%s, %s, %s, %s)")
                data = (rname, raddress, username, pass1)
                cursor1.execute(add_restaurant, data)
                db.commit()
                return redirect(url_for('login'))               
            else:
                data = {}
                data['to_show'] = True
                data["error"] = "Username already exists"
                return render_template("restaurant_register.html", **data)

app.secret_key = '\x1e.\xef\x1bd\xf6~\'\x16=\xfdy\xbc\xf2\xd2\xffb\xba"\x1fO\x9ez\xff'

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=4000, debug=True)

