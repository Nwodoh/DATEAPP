import os
import re
import secrets

class Config:
    DB_NAME = "database.db"
    SECRET_KEY = 'seSSion*Secret*key' # secrets.token_hex(16)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USER_RESTRICTED_FIELDS = ['email', 'password', 'has_details']
    USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_]{1,20}$')
    GENDER_ENUM = ['male', 'female', 'others']
    ORIENTATIONS = ['male', 'female']
    UPLOAD_FOLDER = './uploads'
    UPLOAD_FOLDER = './uploads'
    INTERESTS = ['travel', 'football', 'walking', 'gym', 'movies', 'music', 'tatoos', 'coffee', 'netflix', 'shopping', 'outdoors', 'nightlife', 'food', 'sports', 'universities', 'nerd', 'beer', 'work', 'dogs', 'cats']
    SENDGRID_API_KEY = 'PLACE API KEY HERE'

    USER_IMAGES_UPLOAD_FOLDER = UPLOAD_FOLDER + f'/images/users'
    
class DevelopmentConfig(Config):
    DEBUG = True

config_by_name = dict(
    development=DevelopmentConfig)
