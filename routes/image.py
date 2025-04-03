from flask import Blueprint, send_file
from config import Config

image = Blueprint('image', __name__)

@image.route('/', methods=['GET'])
@image.route('/<img_url>', methods=['GET'])
def get_otp(img_url=''):
    try:
        image_link = f'{Config.USER_IMAGES_UPLOAD_FOLDER}/{img_url}'
        return send_file(image_link)
    except Exception as err:
        image_404 = f'{Config.USER_IMAGES_UPLOAD_FOLDER}/not-found.jpg'
        return send_file(image_404)