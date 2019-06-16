import os
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for
from web import web
from web.forms import AudioForm

ALLOWED_EXTENSION = ['wav']


@web.route('/')
def index():
	return redirect(url_for('upload'))


def allowed_file(filename):
	return "." in filename and \
		filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSION


def check_folder_exist(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)


@web.route('/upload')
def upload():
	return render_template('upload.html', title='Upload Audio')


@web.route('/upload_file', methods=['GET','POST'])
def upload_file():
	if request.method == 'POST':
		if 'file' not in request.files:
			return "File not found"
		file = request.files['file']
		if file.filename == '':
			return 'File not selected'
		if file and allowed_file(file.filename):
			check_folder_exist(os.path.join(web.config['UPLOAD_FOLDER']))
			filename = secure_filename(file.filename)
			file.save(os.path.join(web.config['UPLOAD_FOLDER'], filename))
			return "File successfully uploaded"
		else:
			return "File not supported"
