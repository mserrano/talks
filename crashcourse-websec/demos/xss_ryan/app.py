import json
from flask import Flask, render_template, request, redirect, url_for, abort
app = Flask(__name__)

pastes = []
bins = {}

@app.route('/')
def hello_world():
	return 'Hello World!'

@app.route('/bin/<bin_name>')
def show_bin(bin_name):
	print 'show', bins
	x = dict((i,pastes[i]) for i in bins.get(bin_name, []))
	return render_template('bin.html', name=bin_name, data=json.dumps(x))

@app.route('/post/<int:post_id>')
def show_paste(post_id):
	try:
		x = {post_id:pastes[post_id]}
		return render_template('paste.html', post=post_id, data=json.dumps(x))
	except IndexError:
		abort(404)

@app.route('/make')
def make_paste():
	return render_template('make.html')

@app.route('/make/<bin_name>', methods=['POST'])
def post_paste(bin_name):
	bins.setdefault(bin_name, []).append(len(pastes))
	pastes.append(request.data)
	print 'post', bins
	return url_for('show_bin', bin_name=bin_name)

if __name__ == '__main__':
	app.run(debug=True, host="0.0.0.0")
