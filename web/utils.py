import os
from flask import current_app


def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in current_app.config['ALLOWED_EXTENSION']


def create_folder_if_not_exist(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)
