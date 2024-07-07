import json
from sqlalchemy import ForeignKey
from app import db
from config import Config

class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'))
    like_by = db.Column(db.Integer, ForeignKey('users.id'))
