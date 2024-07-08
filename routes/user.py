from flask import Blueprint, jsonify, session, request
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError
from email_validator import validate_email, EmailNotValidError
from app import db
from config import Config
from models.User import User
from utils.helpers import set_err_args, assign_res, fromIsoStr, haversine
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

@user.route('/', methods=['GET'])
@login_required
def around_point():
    try:
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        if not (lat and lon): raise Exception('Invalid latitude or longitude.', 400)
        lat = int(lat)
        lon = int(lon)
        nearby_users = []

        users = User.query.all()
        for user in users:
            user_location = user.get_location()
            if not user_location or len(user_location) != 2: continue
            user_lat = user_location[0]
            user_lon = user_location[1]
            
            if not (type(user_lat) == float or type(user_lat) == int): continue
            if not (type(user_lon) == float or type(user_lon)) == int: continue

            distance = haversine(user_lat, user_lon, lat, lon)
            print(distance)

            if distance <= 1000:
                nearby_users.append(user.to_dict())

        return jsonify({**assign_res(), 'users': nearby_users})
    except Exception as err:
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code


@user.route('/like/<other_user_id>', methods=['POST'])
@login_required
def like(other_user_id):
    try: 
        other_user_id = int(other_user_id)
        if not other_user_id: raise Exception('No user to like was specified.', 400)
        if other_user_id == current_user.id: raise Exception('You can not like you own profile', 403)

        other_user = User.query.get(other_user_id)
        if not other_user: raise Exception('user to like was not found in our database.', 404)
        current_user.liked_users.append(other_user)
        
        db.session.commit()
        return {**assign_res(), 'otherUser': other_user.to_dict()}
    except IntegrityError as err:
        err_message, err_code = ('You already liked this user.', 403)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code
    except Exception as err:
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code

# https://sqlitebrowser.org/dl/