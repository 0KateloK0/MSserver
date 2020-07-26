from app import app
from flask import render_template, request, url_for, send_from_directory
import json
import os
import subprocess

def checkApplication (id, file):
	PATH = './app/static/tests/archive_{}'.format(id)
	old_path = os.getcwd()
	os.chdir(os.path.abspath(PATH))

	fname = file.filename
	file.save(fname)

	show_files = open('show_tests.txt').read().split()
	result = []
	for test in os.listdir( './tests/' )[::2]:
		print(int(test))
		try:
			 # из-за того что файлы тестов хранятся в формате 01, 02, 03... надо делать это странное преобразование
			show = show_files.index( str(int(test)) ) >= 0
		except ValueError:
			show = False

		expected = open( 'tests/{}.a'.format(test) ).read().split()
		obj = {
			'input': open( 'tests/' + test ).read().split(),
			'expected': expected,
			'show': show
			}

		try:
			process = subprocess.run(fname, stdin=open( 'tests/' + test), stdout=subprocess.PIPE, timeout=2)
			got = process.stdout.decode().split()
			obj['got'] = got
			obj['status'] = 'OK' if got == expected else 'WA'
		except subprocess.TimeoutExpired:
			obj['status'] = 'TL'

		result.append(obj)

	os.remove(fname)
	os.chdir(old_path)
	return result

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index ():
	return render_template('index.html')

@app.route('/file', methods=['GET', 'POST'])
def file ():
	return json.dumps(checkApplication(request.form['task_id'], request.files['file']))