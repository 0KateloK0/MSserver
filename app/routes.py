from app import app
from flask import render_template, request, url_for, send_from_directory
import json
import os
import subprocess
import random

def get_archive (archive_id):
	def get_file_from_archive (filename):
		return open('./app/static/tests/archive_{}/{}'.format(archive_id, filename))
	return get_file_from_archive

# def get_file_from_archive (archive_id, filename):
# 	return open('./app/static/tests/archive_{}/{}'.format(archive_id, filename))


def get_random_file_name ():
	return '%04x.exe' % random.getrandbits(16)

def checkApplication (id, file):
	# old_path = os.getcwd()
	# os.chdir(os.path.abspath(PATH))
	
	get_file = get_archive(id)

	fname = get_random_file_name()
	# just to be sure
	while os.path.exists(fname):
		fname = get_random_file_name()
	file.save(fname)

	show_files = get_file('show_tests.txt').read().split()
	# show_files = open('show_tests.txt').read().split()
	result = []
	for test in os.listdir( './app/static/tests/archive_{}/tests/'.format(id) )[::2]:
		try:
			 # из-за того что файлы тестов хранятся в формате 01, 02, 03... надо делать это странное преобразование
			show = show_files.index( str(int(test)) ) >= 0
		except ValueError:
			show = False

		expected = get_file('tests/{}.a'.format(test) ).read().split() #open( 'tests/{}.a'.format(test) )
		obj = {
			'input': get_file('tests/{}'.format(test) ).read().split(), #open( 'tests/' + test )
			'expected': expected,
			'show': show
			}

		try:
			print(fname)
			process = subprocess.run(fname, stdin=get_file('tests/{}'.format(test)), stdout=subprocess.PIPE, timeout=10) #open( 'tests/' + test)
			got = process.stdout.decode().split()
			obj['got'] = got
			obj['status'] = 'OK' if got == expected else 'WA'
		except subprocess.TimeoutExpired:
			obj['status'] = 'TL'

		result.append(obj)

	os.remove(fname)
	# os.chdir(old_path)
	return result

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index ():
	return render_template('index.html')

@app.route('/file', methods=['GET', 'POST'])
def file ():
	return json.dumps(checkApplication(request.form['task_id'], request.files['file']))