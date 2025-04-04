from flask import Blueprint, send_file
from config import Config

image = Blueprint('image', __name__)

# Handles Any route from the frontend that starts with: `/api/v1/image`
# It's what returns any image that is stored in the /uploads folder and if no image was found for the received URL it returns a default image

@image.route('/', methods=['GET'])
@image.route('/<img_url>', methods=['GET'])
def get_otp(img_url=''):
    try:
        image_link = f'{Config.USER_IMAGES_UPLOAD_FOLDER}/{img_url}'
        return send_file(image_link)
    except Exception as err:
        image_404 = f'{Config.USER_IMAGES_UPLOAD_FOLDER}/not-found.jpg'
        return send_file(image_404)