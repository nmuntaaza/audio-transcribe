import os
from werkzeug.utils import secure_filename
from flask import render_template, request
from web import web
from web.forms import AudioForm

ALLOWED_EXTENSION = set(['wav'])

@web.route('/')
@web.route('/index')
def index():
	return "Hello World"

def allowed_file(filename):
	return "." in filename and \
		filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSION

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
			filename = secure_filename(file.filename)
			file.save(os.path.join(web.config['UPLOAD_FOLDER'], filename))
			return "File Uploaded Successfully"
		else:
			return "File not supported"