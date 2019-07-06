import os
from flask import Flask
from config import Config

# define instance of Flask class
web = Flask(__name__)
web.config.from_object(Config)

# Set Google Credential JSON
credential_path = "kota-108-credential.json"
if os.path.exists(credential_path) and \
        os.path.isfile(credential_path):
    abs_credential_path = os.path.abspath(credential_path)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = abs_credential_path

# import routes from app package
from web import routes
