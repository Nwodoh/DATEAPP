import json
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy import Enum, UniqueConstraint, CheckConstraint
from app import db
from config import Config

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120), unique = True, nullable=False)
    password = db.Column(db.String(25), nullable = False, default='')
    name = db.Column(db.String(2))
    username = db.Column(db.String(20), unique=True)
    image_urls = db.Column(db.String, nullable=True)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(Enum(*Config.GENDER_ENUM, name='gender_enum'))
    about = db.String(db.String(300))
    orientation = db.Column(Enum(*Config.ORIENTATIONS, name='orientation_enum'))
    interests = db.Column(db.String)
    location = db.Column(db.String)
    has_details = db.Column(db.Boolean, nullable=False, default=False)

    # likes = relationship('Like', back_populates='user')

    def __repr__(self):
        return f'Person with email: {self.email} and with password: {self.password}'

    @staticmethod
    def is_valid_username(username):
        return Config.USERNAME_REGEX.match(username) is not None
    
    @staticmethod
    def is_valid_name(name:str=''):
        name_len=len(name)
        return name_len > 0 and name_len < 50

    @staticmethod
    def check_interest(interests:list=[]):
        for interest in interests:
            if not interest in Config.INTERESTS: raise Exception(f'Invalid interest passed `{interest}`.', 403)

    @staticmethod
    def check_location(location:list=[]):
        if not len(location) or len(location) != 2: raise Exception(f'Invalid location passed {location}.', 400)
        if not (type(location[0]) is int and type(location[1]) is int): raise Exception('Invalid location passed.', 400)  
        return True

    def set_image_urls(self, image_urls:list=[]):
        self.image_urls = json.dumps(image_urls)

    def set_interests(self, interests:list=[]):
        self.interests = json.dumps(interests)

    def set_location(self, location:list=[]):
        self.location = json.dumps(location)

    def get_image_urls(self):
        return json.loads(self.image_urls)

    __table_args__ = (
        UniqueConstraint('username', name='uix_user_username'),
        UniqueConstraint('email', name='uix_user_email'),
    )
