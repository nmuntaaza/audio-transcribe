import os
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash, current_app
from web import web
from web.forms import AudioForm
from web import utils
from web.transcribe import transcribe


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
			noise_start = float(request.form.get('noise_start'))
			noise_end = float(request.form.get('noise_end'))
			if noise_start and noise_end:
				utils.create_folder_if_not_exist(os.path.join(web.config['UPLOAD_FOLDER']))
				print(os.path.join(web.config['UPLOAD_FOLDER']))
				filename = secure_filename(file.filename)
				file.save(os.path.join(web.config['UPLOAD_FOLDER'], filename))
				if transcribe.transcribe(filename, noise_start, noise_end, verbose=False):
					flash("File successfully uploaded", "success")
					flash("File successfully trancribed", "success")
				else:
					flash("File successfully uploaded", "success")
					flash("File unsuccessfully trancribed", "error")
				return redirect('/')
			else:
				flash("Noise start time and end time must be given", "error")
				return redirect('/')
		else:
			flash("File not supported, please upload wav file", "error")
			return redirect('/')
