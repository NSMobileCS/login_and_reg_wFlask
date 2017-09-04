#!/home/nrs/venvs/py27flask-env/bin/python
import binascii, md5, os, re
from flask import flash, Flask, redirect, render_template, request, session, url_for
from mysqlconnection import MySQLConnection

app = Flask(__name__)

mysql = MySQLConnection(app, 'logins')

regexes = {
    'first_name': re.compile(r'[A-Z]{1}[a-z]{1,20}'),
    'last_name': re.compile(r'[A-Z]{1}[a-z]{1,20}'),
    'email': re.compile(r'\w{1,10}[\w.]{0,20}@[a-zA-Z]{2,10}[\w.]{0,15}.[a-zA-Z.]{0,15}'),
    'password': re.compile(r'[\W\w]{2,80}'),
}   


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    try:
        query = "SELECT * FROM 'logins' WHERE (email=:useremail)"
        qdata = {'useremail':request.form['email']}
        user = mysql.query_db(query, qdata)
        print dir(user)
    except Exception:
        flash('login fail')
        return redirect('/')
    flash('login success')
    return redirect('/success')


@app.route('/', methods=['POST'])
def validate_new():
    for key, regex in regexes.items():
        if not regex.match(request.form[key]):
            flash('problem with {} field'.format(key))
            return redirect("/")
    if request.form['password'] != request.form['confirm_password']:
        flash('password mismatch')
        return redirect('/')
    salt = binascii.b2a_hex(os.urandom(25))
    pw = md5.new(request.form['password']+salt)
    qdata = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],      
        'hashedpw': pw,
        'pwhash': salt,
        }
    query = """
        INSERT INTO `logins`.`logins`
            (`first_name`,
            `last_name`,
            `email`,
            `hashedpw`,
            `pwhash`) 
            VALUES 
                (:first_name,
                :last_name,
                :email, 
                :hashedpw,
                :pwhash);
            """
    mysql.query_db(query, qdata)
    return redirect('/success')

@app.route('/success')
def success():
    render_template('success.html')    

app.run(debug=True)