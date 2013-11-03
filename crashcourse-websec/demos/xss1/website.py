from flask import Flask
from flask import render_template
from flask import make_response
from flask import request
from flask import session
from flask import g
from flask import redirect,url_for
from hashlib import sha1

app = Flask('website')
app.config['DEBUG'] = True
@app.route("/headers/")
def classes():
  if 'admin' in request.headers:
    return render_template("headers_success.html")
  return render_template("headers_fail.html")

@app.route("/cookies1/")
def projects():
  if 'admin' in request.cookies and request.cookies['admin'] == '1':
    return render_template("cookies_success.html")
  resp = make_response(render_template("cookies_fail.html"))
  resp.set_cookie('admin', '0')
  return resp

@app.route("/cookies2/")
def better_cookies():
  if 'user' in request.cookies and request.cookies['user'] == sha1('admin').hexdigest():
    return render_template("cookies_success.html")
  resp = make_response(render_template("cookies_fail.html"))
  resp.set_cookie('user', sha1('guest').hexdigest())
  return resp

@app.route("/login/", methods=['GET', 'POST'])
def login():
  p = { 'Bob': 'password', 'Eve': 'evil' }
  s = { 'Bob': 'stolen_data1!one', 'Eve': 'Go get Bob\'s secret' }
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    if password != p[username]:
      return render_template("wrong_creds.html")
    session['username'] = username
    resp = make_response(render_template("logged_in.html"))
    resp.set_cookie("secret", s[username])
    return resp
  else:
    return render_template("login.html")

@app.route("/xss/", methods=['GET','POST'])
def xss():
  if 'username' not in session:
    return redirect(url_for('login'))
  if request.method == 'GET':
    f = open("/var/www/app/messages", "r")
    l = []
    for line in f:
      l += [line]
    f.close()
    return render_template("messages.html", l=l)
  else:
    msg = request.form['msg']
    f = open("/var/www/app/messages", "a")
    f.write(session['username'] + ': ' + msg + '\n')
    f.close()
    return redirect(url_for('xss'))

@app.route("/")
def hello():
  return "<html>Hi.</html>"

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWf/o?RT'
if __name__ == "__main__":
  app.run(host='0.0.0.0',port=80)
