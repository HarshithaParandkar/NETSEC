from flask import Flask, request, redirect, url_for, session, render_template
from flask_mysqldb import MySQL
import MySQLdb.cursors

# Initialize Flask app
web = Flask(__name__)

# MySQL configuration
web.config['MYSQL_HOST'] = 'localhost'
web.config['MYSQL_USER'] = 'root'
web.config['MYSQL_PASSWORD'] = 'SRIv#4321'
web.config['MYSQL_DB'] = 'UserDB'

mysql = MySQL(web)

@web.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            msg = 'Invalid username/password'
    return render_template('login.html', msg=msg)