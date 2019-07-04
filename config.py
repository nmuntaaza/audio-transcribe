import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'kota8kudululus'
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER') or 'uploaded_file/'
    ALLOWED_EXTENSION = ['wav']
    TEMP_FOLDER = os.getenv('TEMP_FOLDER') or 'wavtemp/'
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS') or 'kota-108-credential.json'
