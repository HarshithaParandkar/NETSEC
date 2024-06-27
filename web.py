import os
import psutil
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_socketio import SocketIO
import MySQLdb.cursors
import logging
from threading import Thread
import netTrack

app = Flask(__name__)
CORS(app)
app.secret_key = 'secret#'
socketio = SocketIO(app)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'SRIv#4321'
app.config['MYSQL_DB'] = 'UserDB'

mysql = MySQL(app)

# Sniff module import and SocketIO initialization
import sniff
sniff.socketio = socketio

@app.route('/data')
def data():
    return jsonify(sniff.packets_data)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
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

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    user_id = session['id']

    if request.method == 'POST':
        username = request.form['username']
        bio = request.form['bio']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        age = request.form['age']
        
        cursor.execute('UPDATE users SET username = %s, bio = %s, email = %s, phone = %s, address = %s, age = %s WHERE id = %s',
                       (username, bio, email, phone, address, age, user_id))
        mysql.connection.commit()
        return redirect(url_for('profile'))

    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    account = cursor.fetchone()

    return render_template('profile.html', account=account)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        bio = request.form['bio']
        phone = request.form['phone']
        address = request.form['address']
        age = request.form['age']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO users (username, email, password, bio, phone, address, age) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                       (username, email, password, bio, phone, address, age))
        mysql.connection.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/profile_page')
def profile_page():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/', methods=["GET"])
def main():
    if 'loggedin' in session:
        username = session.get('username')
        return render_template('main.html', username=username)
    else:
        return redirect(url_for('login'))

# Rename this route function to avoid conflict with the module name
@app.route('/netTrack', methods=["POST", "GET"])
def netTrack_page():
    return render_template('netTrack.html')

@app.route('/netBlaze', methods=["POST", "GET"])
def netBlaze():
    return render_template('netBlaze.html')

@app.route('/netScan', methods=["POST", "GET"])
def netScan():
    return render_template('netScan.html')

@app.route('/network_data', methods=['GET'])
def network_data():
    try:
        return jsonify(netTrack.network_data)
    except Exception as e:
        return jsonify({
            'error': str(e)
        })

@app.route('/speedtest', methods=['GET'])
def speedtest():
    return render_template('speedtest.html')

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # Start the packet sniffer in a separate thread
    sniffer_thread = Thread(target=sniff.start_sniffing)
    sniffer_thread.start()

    # Start the network data updater in a separate thread
    netTrack.update_network_data()

    # Start Flask-SocketIO server on port 5000
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
