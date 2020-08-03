from app import app
from flask import render_template, request, make_response
import json
import os
import subprocess
import random

def get_archive_function (archive_id):
	def get_file_from_archive (filename):
		return open('./app/static/tests/archive_{}/{}'.format(archive_id, filename))
	return get_file_from_archive

def get_random_file_name ():
	return '%04x.exe' % random.getrandbits(16)

def checkApplication (id, file):
	get_file = get_archive_function(id)
	fname = get_random_file_name()
	# только для уверенности
	while os.path.exists(fname):
		fname = get_random_file_name()
	file.save(fname)

	show_files = get_file('show_tests.txt').read().split()
	result = []
	for test in os.listdir( './app/static/tests/archive_{}/tests/'.format(id) )[::2]:
		try:
			 # из-за того что файлы тестов хранятся в формате 01, 02, 03... надо делать это странное преобразование
			show = show_files.index( str(int(test)) ) >= 0
		except ValueError:
			show = False

		expected = get_file('tests/{}.a'.format(test) ).read().split()
		obj = {
			'input': get_file('tests/{}'.format(test) ).read().split(),
			'expected': expected,
			'show': show
			}

		try:
			process = subprocess.run(fname, stdin=get_file('tests/{}'.format(test)), stdout=subprocess.PIPE, timeout=2)
			got = process.stdout.decode().split()
			obj['got'] = got
			obj['status'] = 'OK' if got == expected else 'WA'
		except subprocess.TimeoutExpired:
			obj['status'] = 'TL'
		except OSError:
			obj['status'] = 'ER'

		result.append(obj)

	os.remove(fname)
	return result

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index ():
	return render_template('index.html')

@app.route('/file', methods=['GET', 'POST'])
def file ():
	if request.method == 'POST':
		file = request.files['file']
		task_id = request.form['task_id']
		if not file:
			return make_response('No file', 400)
		elif not task_id:
			return make_response('No task id', 400)
		else:
			test_result = checkApplication(task_id, file)
			return json.dumps(test_result)
	else:
		return make_response('Only POST requests are allowed', 400)