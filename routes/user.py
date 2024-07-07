from flask import Blueprint, jsonify, session, request
from flask_login import current_user, login_required
from email_validator import validate_email, EmailNotValidError
from app import db
from config import Config
from models.User import User
from utils.helpers import set_err_args, assign_res, fromIsoStr
from utils.ImageManager import ImageManager

user = Blueprint('user', __name__)

@user.route('/', methods=['POST'])
@login_required
def update_me():
    try:
        email = current_user.email
        if not email: raise EmailNotValidError()

        img_files = request.files.getlist('images')
        if len(img_files) > 0:
            image_urls = ImageManager().save_images(img_files)
            current_user.set_image_urls(image_urls)

        data = request.get_json()
        for key, value in data.items():
            if key in Config.USER_RESTRICTED_FIELDS: continue
            if key == 'name' and not current_user.is_valid_name(value): raise Exception('Invalid Username', 400)
            if key == 'username' and not current_user.is_valid_username(value): raise Exception('Invalid Username', 400)
            if key == 'gender' and not value in Config.GENDER_ENUM: raise Exception(f'Invalid Gender {value}.', 400)
            if key == 'orientation' and not value in Config.ORIENTATIONS: raise Exception(f'Invalid Orientation {value}.', 400)
            if key == 'date_of_birth': value = fromIsoStr(value)
            if key == 'interests':
                current_user.check_interest(value)
                current_user.set_interests(value)
                continue
            if key == 'location':
                current_user.check_location(value)
                current_user.set_location(value)
                continue
            if hasattr(current_user, key):
                setattr(current_user, key, value)

        db.session.commit()

        return jsonify({**assign_res()})
    except EmailNotValidError:
        return jsonify({**assign_res('error'), 'message': 'Email is Invalid.'}), 400
    except Exception as err:
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code

@user.route('/', methods=['POST'])
def around_me():
    pass