import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'kota8kudululus'
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER') or 'uploaded_file/'