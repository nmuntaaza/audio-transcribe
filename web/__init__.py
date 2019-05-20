from flask import Flask
from config import Config

UPLOAD_FOLDER = 'uploaded_file/'

# define instance of Flask class
web = Flask(__name__)
web.config.from_object(Config)
web.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# import routes from app package
from web import routes