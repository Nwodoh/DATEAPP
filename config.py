import os
import re
from dotenv import load_dotenv

load_dotenv(".env")  # Load the variables from the file

class Config:
    DB_NAME = "database.db"
    SECRET_KEY = 'seSSion*Secret*key' # secrets.token_hex(16)
    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USER_RESTRICTED_FIELDS = ['email', 'password', 'has_details']
    USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_]{1,20}$')
    GENDER_ENUM = ['male', 'female', 'others']
    ORIENTATIONS = ['male', 'female']
    UPLOAD_FOLDER = './uploads'
    INTERESTS = ['travel', 'football', 'walking', 'gym', 'movies', 'music', 'tatoos', 'coffee', 'netflix', 'shopping', 'outdoors', 'nightlife', 'food', 'sports', 'universities', 'nerd', 'beer', 'work', 'dogs', 'cats']
    FIREBASE_WEB_API_URL = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={os.getenv("FIREBASE_WEB_API_KEY")}'
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SAMESITE = "None"

    USER_IMAGES_UPLOAD_FOLDER = UPLOAD_FOLDER + f'/images/users'
    
class DevelopmentConfig(Config):
    DEBUG = True

config_by_name = dict(
    development=DevelopmentConfig)
