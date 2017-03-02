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

@app.route("/deleteitem", methods=['POST'])
def delitem():
    if request.method == "POST":
        if 'username' in session:
            k = request.form['K']
            cursor.execute(("DELETE FROM `menu` WHERE `menu_id` = %s"),(k))
            db.commit()
            return "Item successfully removed"
        else:
            return redirect(url_for('login'))

@app.route("/modifystatus", methods=['POST'])
def modifystatus():
    if request.method == "POST":
        if 'username' in session:
            status = request.form['status']
            order_id = request.form['order_id']
            cursor.execute(("UPDATE `order` SET `status`= %s WHERE `order_id`=%s"),(status, order_id))
            db.commit()
            return "Item status updated"
        else:
            return redirect(url_for('login'))

@app.route("/deleteuser", methods=['POST'])
def deluser():
    if request.method == "POST":
        if 'username' in session:
            k = request.form['K']
            cursor.execute(("DELETE FROM `users` WHERE `id` = %s"),(k))
            db.commit()
            return "User successfully removed"
        else:
            return redirect(url_for('login'))

@app.route("/deleteres", methods=['POST'])
def delres():
    if request.method == "POST":
        if 'username' in session:
            k = request.form['K']
            cursor.execute(("DELETE FROM `restaurants` WHERE `username` = %s"),(k))
            db.commit()
            return "Restaurant successfully removed"
        else:
            return redirect(url_for('login'))

@app.route("/additem", methods=['POST'])
def additem():
    if request.method == "POST":
        if 'username' in session:
            username = escape(session['username'])
            iname = request.form['iname']
            iprice = request.form['iprice']
            cat = request.form['cat']
            type1 = request.form['group1']
            cursor.execute(("INSERT into `menu` (`username`,`name`,`price`,`type`,`category`) VALUES (%s,%s,%s,%s,%s)"),(username, iname, iprice, type1, cat))
            db.commit()
            address = escape(session['address'])
            name = escape(session['name'])
            return render_template('rhome.html', rname=name, username=username, address=address, error="Item successfully added")
        else:
            return redirect(url_for('login'))
 
@app.route("/r", methods=['GET'])
def r():
    if request.method == "GET":
        if 'username' in session:
            data = []
            data.append(session['username']);
            data.append(session['name']);
            data.append(session['address']);
            return Response(json.dumps(data), mimetype='application/json')
        else:
            return redirect(url_for('login'))

@app.route("/rhome", methods=['GET', 'POST'])
def rhome():
    if request.method == "GET":
        if 'username' in session:
            username_session = escape(session['username']).capitalize()
            address = escape(session['address'])
            name = escape(session['name'])
            return render_template('rhome.html', rname=name, username=username_session, userid=address)
        else:
            return redirect(url_for('login'))
    elif request.method == "POST":
        error = None

@app.route("/rhome/orders", methods=['GET', 'POST'])
def orders():
    if request.method == "GET":
        if 'username' in session:
            username_session = escape(session['username'])
            address = escape(session['address'])
            name = escape(session['name'])
            return render_template('orders.html', rname=name, username=username_session, address=address)
        else:
            return redirect(url_for('login'))
    elif request.method == "POST":
        error = None

@app.route("/orders", methods=['GET'])
def getOrders():
    if request.method == "GET":
        if 'username' in session:
            r_uname = escape(session['username'])
            cursor.execute(("SELECT * from `order` WHERE `res_uname` = %s"), (r_uname))
            data = cursor.fetchall()
            data2 = []
            for t in data:
                cursor.execute(("SELECT * from `order_details` WHERE `order_id` = %s"), (list(t)[5]))
                temp = cursor.fetchall()
                f = []
                x = list(temp)
                cursor1 = db.cursor()
                cursor1.execute(("SELECT `user_id` from `order` WHERE `order_id` = %s"),(list(t)[5]))
                user_id = list(cursor1.fetchone())[0]
                for r in x:
                    y = list(r)
                    y.append(user_id)
                    f.append(y)
                print f
                data2.append(f)
            return Response(json.dumps(data2), mimetype='application/json')
        else:
            return redirect(url_for('login'))

@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if request.method == "GET":
        return render_template('admin.html', error = None)
    elif request.method == "POST":
        error = None

@app.route("/users", methods=['GET'])
def users():
    if request.method == "GET":
        if 'username' in session:
            cursor.execute("SELECT * from users")
            data = cursor.fetchall()
            return Response(json.dumps(data), mimetype='application/json')
        else:
            return redirect(url_for('login'))

@app.route("/restaurants", methods=['GET'])
def restaurants1():
    if request.method == "GET":
        if 'username' in session:
            cursor.execute("SELECT * from restaurants")
            data = cursor.fetchall()
            return Response(json.dumps(data), mimetype='application/json')
        else:
            return redirect(url_for('login'))

@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html', error = None)
    elif request.method == "POST":
        error = None
        username = request.form['username']
        password = request.form['password']
        selected = request.form['group1']
        if selected == "1":
            print "user"
            cursor.execute(("SELECT * from users where username=%s AND password=%s"), (username, password))
            data = cursor.fetchone()
            if data is None:
                error = "Invalid Credentials"
            if error is None:
                session['username'] = username
                session['id'] = list(data)[0]
                session['fname'] = list(data)[1]
                if username == "admin":
                    return redirect(url_for('admin')) 
                else:   
                    return redirect(url_for('home'))
            else:
                return render_template("login.html", error = error)
        else:
            print "res"
            cursor.execute(("SELECT * from restaurants where username=%s AND password=%s"), (username, password))
            data = cursor.fetchone()
            if data is None:
                error = "Invalid Credentials"
            if error is None:
                session['username'] = username
                session['name'] = list(data)[2]
                session['address'] = list(data)[3]
                return redirect(url_for('rhome'))
            else:
                return render_template("login.html", error = error)

@app.route("/home", methods=['GET', 'POST'])
def home():
    if request.method == "GET":
        if 'username' in session:
            username_session = escape(session['username']).capitalize()
            username_id = escape(session['id'])
            fname = escape(session['fname'])
            return render_template('home.html', fname=fname, username=username_session, userid=username_id)
        else:
            return redirect(url_for('login'))
    elif request.method == "POST":
        error = None

@app.route("/cuisines", methods=['GET'])
def cuisines():
    if request.method == "GET":
        if 'username' in session:
            cursor.execute("SELECT * from categories")
            data = cursor.fetchall()
            return Response(json.dumps(dict(data)), mimetype='application/json')
        else:
            return redirect(url_for('login'))

@app.route("/cuisines/<cid>", methods=['GET'])
def getRes(cid):
    if request.method == "GET":
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
    if request.method == "GET":
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
    if request.method == "GET":
        if 'username' in session:
            cursor.execute(("SELECT * from menu WHERE username = %s ORDER BY category DESC"), (rid))
            data = cursor.fetchall()
            return Response(json.dumps(data), mimetype='application/json')
        else:
            return redirect(url_for('login'))

@app.route("/home/cuisines/<cid>/<username>", methods=['GET'])
def menu(cid, username):
    if request.method == "GET":
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

@app.route("/home/cuisines/<cid>/<username>/cart", methods=['GET', 'POST'])
def cart(cid, username):
    if request.method == "GET":
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
                return render_template("cart.html", res_uname= username, res_name=list(data1)[0], cuisine_id = cid, cuisine_name=list(data)[0], fname=fname, username=username_session, userid=username_id)
        else:
            return redirect(url_for('login'))
    elif request.method == "POST":
        return "POST"

@app.route("/home/cuisines/<cid>/<username>/checkout", methods=['GET', 'POST'])
def checkout(cid, username):
    if request.method == "GET":
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
                return render_template("checkout.html", res_uname= username, res_name=list(data1)[0], cuisine_id = cid, cuisine_name=list(data)[0], fname=fname, username=username_session, userid=username_id)
        else:
            return redirect(url_for('login'))
    elif request.method == "POST":
        return "POST"

@app.route("/home/cuisines/<cid>/<res_uname>/order", methods=['POST'])
def order(cid, res_uname):
    if request.method == "POST":
        iname = request.form['iname'].split(',')
        iprice = request.form['iprice'].split(',')
        iquan = request.form['iquan'].split(',')
        fname = request.form['fname']
        telephone = request.form['telephone']
        address = request.form['address']
        user_id = escape(session['id'])
        query1 = ("INSERT INTO `order` "
                   "(`user_id`, `res_uname`, `fname`, `telephone`, `address`, `status`) "
                   "VALUES (%s, %s, %s, %s, %s, %s)")
        cursor = db.cursor()
        cursor.execute(query1, (user_id, res_uname, fname, telephone, address, "Acknowledged"))
        db.commit()
        cursor = db.cursor()
        cursor.execute("SELECT `order_id` FROM `order` ORDER BY order_id DESC LIMIT 1;")
        data = cursor.fetchone()
        order_id = list(data)[0]
        for einame,eiprice,eiquan in zip(iname, iprice, iquan):
            if eiquan != "0":
                cursor = db.cursor()
                cursor.execute(("INSERT INTO `order_details` (`order_id`, `iname`, `iprice`, `iquan`) VALUES (%s, %s, %s, %s)"),(order_id, einame, eiprice, eiquan))
                db.commit()
        return "Order placed successfully"
    else:
        return "Invalid request"

@app.route("/history", methods=['GET'])
def getHistory():
    if request.method == "GET":
        if 'username' in session:
            userid = escape(session['id'])
            cursor.execute(("SELECT * from `order` WHERE `user_id` = %s"), (userid))
            data = cursor.fetchall()
            data2 = []
            for t in data:
                cursor.execute(("SELECT * from `order_details` WHERE `order_id` = %s"), (list(t)[5]))
                temp = cursor.fetchall()
                f = []
                x = list(temp)
                cursor1 = db.cursor()
                cursor1.execute(("SELECT `name` from `restaurants` WHERE `username` = %s"),(list(t)[1]))
                rname = list(cursor1.fetchone())[0]
                cursor2 = db.cursor()
                cursor2.execute(("SELECT `status` from `order` WHERE `order_id` = %s"),(list(t)[5]))
                pik = list(cursor2.fetchone())[0]
                for r in x:
                    y = list(r)
                    y.append(rname)
                    y.append(pik)
                    f.append(y)
                data2.append(f)
            return Response(json.dumps(data2), mimetype='application/json')
        else:
            return redirect(url_for('login'))

@app.route("/home/order/history", methods=['GET', 'POST'])
def history():
    if request.method == "GET":
        if 'username' in session:
            username_session = escape(session['username']).capitalize()
            username_id = escape(session['id'])
            fname = escape(session['fname'])
            return render_template("history.html", fname=fname, username=username_session, userid=username_id)
        else:
            return redirect(url_for('login'))
    elif request.method == "POST":
        return "POST"

@app.route("/restaurant/register", methods=['GET', 'POST'])
def rreg():
    if request.method == "GET":
        return render_template('restaurant_register.html')
    elif request.method == "POST":
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

