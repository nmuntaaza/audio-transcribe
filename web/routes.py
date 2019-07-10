import os
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, flash, session, jsonify
from web import web
from web import utils
from web.transcribe import transcribe


@web.route('/test', methods=['GET', 'POST'])
def test():
    return render_template('test.html', title="Audio Transcribe", step='upload')


@web.route('/')
def home():
    session['step'] = 'upload'
    return render_template('template.html', title='Audio Transcribe', step='upload')


@web.route('/process_audio', methods=['POST', 'GET'])
def process_audio():
    if session.get('step') != 'process_audio':
        flash('Please upload your file first', 'error')
        return redirect('/')

    if session.get('filename') != '':
        generated_dialogue = transcribe.transcribe(session.get('filename'))
        if generated_dialogue:
            session['step'] = 'transcript'
            return render_template('template.html',
                                   title='Audio Transcribe',
                                   generated_dialogue=generated_dialogue)
    else:
        flash('Please upload your file first', 'error')
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
            # return render_template('template.html', title='Audio Transcribe', step='process_audio', filename=filename)
            return render_template('test.html', title='Audio Transcribe', step='process_audio', filename=filename)
        else:
            flash('File not supported, please upload wav file')
            return redirect('/')


@web.route('/get_session', methods=['GET'])
def get_session():
    if request.method == 'GET':
        data = {}
        try:
            data['step'] = session.get('step')
            data['filename'] = session.get('filename')
        except:
            pass
        return jsonify(data)
