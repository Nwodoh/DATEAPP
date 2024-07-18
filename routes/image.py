from flask import Blueprint, send_file, jsonify, session, request 
from flask_login import login_required
from config import Config
from app import db

image = Blueprint('image', __name__)

@image.route('/<img_url>', methods=['GET'])
def get_otp(img_url):
    try:
        image_link = f'{Config.USER_IMAGES_UPLOAD_FOLDER}/{img_url}'
        print(image_link)
        return send_file(image_link)
    except Exception as err:
        image_404 = f'{Config.USER_IMAGES_UPLOAD_FOLDER}/not-found.jpg'
        return send_file(image_404)