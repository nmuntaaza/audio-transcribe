import os
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, flash, session, jsonify
from web import web
from web import utils
from web.transcribe import transcribe


@web.route('/')
def index():
    return render_template('template.html', title='Audio Transcribe', step='upload')


@web.route('/process', methods=['POST'])
def process():
    if request.method == 'POST':
        filename = request.form.get('filename')
        result = {}

        if filename == '':
            result['status'] = 500
            result['message'] = 'Please upload your file first'
            return jsonify(result)
        try:
            generated_audio = transcribe.transcribe(filename, verbose=True)
            if type(generated_audio) is list and \
                    isinstance(generated_audio, list) and \
                    generated_audio is not None:
                result['status'] = 200
                result['message'] = 'Processing success'
                result['data'] = generated_audio
            else:
                result['status'] = 500
                result['message'] = 'Processing failed'

            return jsonify(result)
        except Exception as e:
            print(e)
            result['status'] = 500
            result['message'] = 'Processing failed'
            return jsonify(result)


@DeprecationWarning
@web.route('/process_audio', methods=['POST'])
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
            flash("File name empty or not selected", "error")
            return redirect('/')

        if not utils.allowed_file(file.filename):
            flash('File not supported, please upload wav file')
            return redirect('/')

        utils.create_folder_if_not_exist(os.path.join(web.config['UPLOAD_FOLDER']))
        filename = secure_filename(file.filename)
        file.save(os.path.join(web.config['UPLOAD_FOLDER'], filename))
        return render_template('template.html', title='Audio Transcribe', step='process_audio', filename=filename)


@web.route('/get_session', methods=['GET'])
def get_session():
    if request.method == 'GET':
        data = {
            "step": session.get('step'),
            "filename": session.get("filename")
        }

        return jsonify(data)
