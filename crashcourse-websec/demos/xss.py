from flask import Flask, request, session, render_template, redirect, url_for
from json import dumps as tojson
from hashlib import sha1
from uuid import uuid4 as uuid
import MySQLdb
import re

app = Flask('website')
app.config['DEBUG'] = True
secret_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

def logged_in():
  username = request.cookies.get('username')
  if username is None:
    return False
  secret = request.cookies.get('secret')
  if secret is None:
    return False
  if secret == sha1(secret_key + username).hexdigest():
    return True
  return False

app.jinja_env.globals['logged_in'] = logged_in

@app.before_request
def get_database_conn():
  g.db = MySQLdb.connect(host="localhost", user="xss1",
                         passwd="XXXXXXXXXXXXXXXXXX", db="xss1")

@app.teardown_request
def close_database_conn():
  db = getattr(g, 'db', None)
  if db is not None:
    db.close()

@app.route("/login/", methods=["GET", "POST"])
def login():
  """Log the given user in"""
  if request.method == 'POST':
    username = request.form['username'].upper()
    if username == '':
      return render_template("login_failed.html", msg="Invalid username!")
    password = request.form['password']
    c = g.db.cursor()
    c.execute("SELECT id, sha_pass_hash FROM accounts WHERE username=%s LIMIT 1",
              username)
    rows = c.fetchall()
    c.close()
    if len(rows) == 0:
      return render_template("login_failed.html", msg="Unknown user!")
    i,p = rows[0]
    hsh = sha1(username + ':' + password).hexdigest().upper()
    if hsh == p:
      # yay successful login
      resp = make_response(render_template("login_success.html"))
      resp.set_cookie('username', username)
      resp.set_cookie('secret', sha1(secret_key + username).hexdigest())
      return resp
    else:
      return render_template("login_failed.html", msg="Wrong password!")
  else:
    return render_template("login.html")

@app.route("/logout/")
def logout():
  """Log the given user out"""
  resp = redirect(url_for('idx'))
  resp.set_cookie('username', '', expires=0)
  resp.set_cookie('secret', '', expires=0)
  return resp

@app.route("/register/", methods=["GET", "POST"])
def register():
  """Register a user"""
  if request.method == 'POST':
    # usernames are case-insensitive to avoid nonsense.
    username = request.form['username'].upper()
    if username == '':
      return render_template("reg_failed.html", msg="Invalid username!")
    password = request.form['password']
    # passwords are case-sensitive, because that's desirable.
    hsh = sha1(username + ':' + password).hexdigest().upper()
    success = False
    try:
      c = g.db.cursor()
      c.execute("INSERT INTO accounts (username, sha_pass_hash) VALUES (%s,%s)",
                (username, hsh))
      c.close()
      g.db.commit()
      success = True
    except:
      pass
    if success:
      return render_template("registered.html")
    else:
      return render_template("reg_failed.html", msg="Username in use or database error!")
  else:
    return render_template("register.html")

@app.route("/message/<int:m>")
def message(m):
  if not logged_in():
    return render_template("read_failed.html", msg="Must be logged in!")
  try:
    c = g.db.cursor()
    user = request.cookies.get('username')
    c.execute("SELECT src, msg FROM messages WHERE id=%s AND dst=%s LIMIT 1", (m, user))
    rows = c.fetchall()
    c.close()
    success = True
  except:
    success = False
  if success:
    msg = row[0]
    src = msg[0]
    txt = msg[1]
    return render_template("read.html", msg=txt, src=src)
  else:
    return render_template("read_failed.html", msg="Message not found!")

@app.route("/messages/")
def messages():
  if not logged_in():
    return render_template("list_failed.html", msg="Must be logged in!")
  try:
    c = g.db.cursor()
    user = request.cookies.get('username')
    c.execute("SELECT id FROM messages WHERE dst=%s LIMIT 1", user)
    rows = c.fetchall()
    c.close()
    success = True
  except:
    success = False
  if success:
    return render_template("list.html", data=rows)
  else:
    return render_template("list_failed.html", msg="Message not found!")

@app.route("/send/", methods=["GET", "POST"])
def send():
  if request.method == 'POST':
    if not logged_in():
      return render_template("send_failed.html", msg="Must be logged in!")
    username = request.cookies.get('username')
    msg = request.form['msg']
    dst = request.form['dst']
    success = False
    try:
      c = g.db.cursor()
      c.execute("SELECT 1 FROM accounts WHERE username=%s", dst)
      rows = c.fetchall()
      c.close()
      if len(rows) > 0:
        c = g.db.cursor()
        c.execute("INSERT INTO messages (src, dst, msg) VALUES (%s,%s,%s)", (username, tgt, msg))
        c.close()
        g.db.commit()
        success = True
    except:
      pass
    if success:
      return render_template("sent.html", target=tgt)
    else:
      return render_template("send_failed.html", msg="Unknown target!")
  else:
    if not logged_in():
      return render_template("send_failed.html", msg="Must be logged in!")
    return render_template("send.html")

@app.route("/")
def idx():
  return render_template("index.html")
