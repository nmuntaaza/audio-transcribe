from flask import Flask
from config import Config

# define instance of Flask class
web = Flask(__name__)
web.config.from_object(Config)

# import routes from app package
from web import routes