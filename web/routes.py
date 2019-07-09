import os
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash, current_app, session
from web import web
from web import utils
from web.transcribe import transcribe


@web.route('/')
def home():
    session['step'] = 'upload'
    return render_template('template.html', title='Audio Transcribe')


@web.route('/process_audio', methods=['POST', 'GET'])
def process_audio():
    if session.get('step') != 'process_audio':
        flash('Please upload your file first')
        return redirect('/')

    if session.get('filename') != '':
        generated_dialogue = transcribe.transcribe(session.get('filename'))
        if generated_dialogue:
            session['step'] = 'transcript'
            return render_template('template.html', title='Audio Transcribe', generated_dialogue=generated_dialogue)
    else:
        flash('Please upload your file first')
        return redirect('/')


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

        if utils.allowed_file(file.filename):
            utils.create_folder_if_not_exist(os.path.join(web.config['UPLOAD_FOLDER']))
            filename = secure_filename(file.filename)
            file.save(os.path.join(web.config['UPLOAD_FOLDER'], filename))
            session['step'] = 'process_audio'
            session['filename'] = filename
            return render_template('template.html', title='Audio Transcribe')
        else:
            flash('File not supported, please upload wav file')
            return redirect('/')
