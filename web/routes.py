import os
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash
from web import web
from web.forms import AudioForm
from web.transcribe import audio_segmentation
from web import utils

@web.route('/')
def upload():
	return render_template('upload.html', title='Upload Audio')


@web.route('/upload_file', methods=['POST'])
def upload_file():
	if request.method == 'POST':
		if 'file' not in request.files:
			flash("File not found", "error")
			return redirect('/')
		file = request.files['file']
		if file.filename == '':
			flash("File not selected", "error")
			return redirect('/')
		if file and utils.allowed_file(file.filename):
			utils.check_folder_exist(os.path.join(web.config['UPLOAD_FOLDER']))
			filename = secure_filename(file.filename)
			file.save(os.path.join(web.config['UPLOAD_FOLDER'], filename))
			flash("File successfully uploaded", "success")
			return redirect('/')
		else:
			flash("File not supported, please upload wav file", "error")
			return redirect('/')


@web.route('/test')
def test():
	test = audio_segmentation.test()
	return render_template('test.html', test=test)
