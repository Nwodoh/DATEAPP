from config import Config
from PIL import Image
from flask import Blueprint, jsonify, request, g
from firebase_admin import firestore
from email_validator import EmailNotValidError
from utils.FBQueries import FBQueries, firebase_auth_required
from utils.helpers import set_err_args, assign_res, haversine, add_random_decimal
from utils.ImageManager import ImageManager
import io
import base64

user = Blueprint('user', __name__)


# Handles Any route from the frontend that starts with: `/api/v1/user`
# Routes for getting, updating, liking and so on. Anything solely user related. 

@user.route('/user/', defaults={'user_id': None}, methods=['GET'])
@user.route('/user/<user_id>', methods=['GET'])
@firebase_auth_required
def get_me(user_id):
    try:
        user = {}
        if user_id: user = FBQueries.get_user(user_id)
        else: user = FBQueries().get_user_by_email(g.current_user['email'], with_likes=True)

        return jsonify({**assign_res(), 'user': user})
    except Exception as err:
        print(err)
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code


@user.route('/', methods=['POST'])
@firebase_auth_required
def update_me():
    try:
        email = g.current_user['email']
        if not email: raise EmailNotValidError()

        profile_image = request.json.get('profileImage') or ''
        background_image = request.json.get('backgroundImage') or ''

        if profile_image and profile_image.get('image') and profile_image.get('filename'): 
            filename = profile_image.get('filename')
            profile_image = base64.b64decode(profile_image.get('image'))
            profile_image = Image.open(io.BytesIO(profile_image))
            profile_image.filename = filename
        if background_image and background_image.get('image') and background_image.get('filename'): 
            filename = background_image.get('filename')
            background_image = base64.b64decode(background_image.get('image'))
            background_image = Image.open(io.BytesIO(background_image))
            background_image.filename = filename

        img_files = [profile_image, background_image]

        update_data = {}
        if len(img_files) > 0:
            image_urls = ImageManager().save_images(img_files)
            while len(image_urls) <= 2: image_urls.append(None)
            if len(image_urls): 
                if(profile_image): update_data['profile_image'] = image_urls[0]
                if(background_image): update_data['background_image'] = image_urls[1] or image_urls[0]
        
        data = request.get_json()
        for key, value in data.items():
            if key in Config.USER_RESTRICTED_FIELDS: continue
            if key == 'name' and value and (len(value) < 1 or len(value) > 50): raise Exception('Invalid Username', 400)
            if key == 'username' and value and not Config.USERNAME_REGEX.match(value) is not None: raise Exception('Invalid Username', 400)
            if key == 'gender' and value and not value in Config.GENDER_ENUM: raise Exception(f'Invalid Gender {value}.', 400)
            if key == 'orientation' and not value in Config.ORIENTATIONS: raise Exception(f'Invalid Orientation {value}.', 400)
            if key == 'location':
                if not len(value) or len(value) != 2: raise Exception(f'Invalid Location passed {value}.', 400)
                if not ((type(value[0]) is int or type(value[0]) is float) and (type(value[1]) is int or type(value[1]) is float)): raise Exception('Invalid location passed.', 400)  
                # LINE OF CODE ADDS A BIT OF RANDOMNESS TO LOCATION - COMMENT OR REMOVE WHEN NOT IN USE
                value = add_random_decimal(value) 
            if key in FBQueries.user_dict({}) and value:
                update_data[key] = value
        user = FBQueries().update_me(update_data)

        return jsonify({**assign_res(), 'user': user})
    except EmailNotValidError:
        return jsonify({**assign_res('error'), 'message': 'Email is Invalid.'}), 400
    except Exception as err:
        print(err)
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code

@user.route('/search/<search_str>', methods=['GET'])
@firebase_auth_required
def query_users(search_str):
    try:
        results = FBQueries.query_users(search_str)
        return jsonify({**assign_res(), 'results': results})
    except Exception as err:
        print(err)
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code

@user.route('/', methods=['GET'])
@firebase_auth_required
def around_point():
    try:
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        if not (lat and lon): raise Exception('Invalid latitude or longitude.', 400)
        lat = float(lat)
        lon = float(lon)
        nearby_users = []

        users = FBQueries.get_all_users()
        for user in users:
            user_location = user['location']
            if not user_location or len(user_location) != 2: continue
            user_lat = user_location[0]
            user_lon = user_location[1]

            if not (type(user_lat) == float or type(user_lat) == int): continue
            if not (type(user_lon) == float or type(user_lon) == int): continue

            distance = haversine(user_lat, user_lon, lat, lon)

            if distance <= 100000:
                nearby_users.append(user)

        return jsonify({**assign_res(), 'users': nearby_users, 'results': len(nearby_users)})
    except Exception as err:
        print(err)
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code


@user.route('/like/<other_user_id>', methods=['POST'])
@firebase_auth_required
def like(other_user_id):
    try: 
        if not other_user_id: raise Exception('No user to like was specified.', 400)

        other_user = FBQueries().like(other_user_id)
        
        return {**assign_res(), 'otherUser': other_user}
    except Exception as err:
        print(err)
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code

@user.route('/like/<other_user_id>', methods=['DELETE'])
@firebase_auth_required
def remove_like(other_user_id):
    try: 
        if not other_user_id: raise Exception('No user to Unlike was specified.', 400)

        other_user = FBQueries().remove_like(other_user_id)
        
        return {**assign_res(), 'otherUser': other_user}
    except Exception as err:
        print(err)
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code

# https://sqlitebrowser.org/dl/

# from flask import Blueprint, jsonify, session, request
# from flask_login import current_user, login_required
# from PIL import Image
# import io
# from sqlalchemy.exc import IntegrityError
# from email_validator import EmailNotValidError
# from app import db
# from config import Config
# from models.User import User
# from utils.helpers import set_err_args, assign_res, fromIsoStr, haversine
# from utils.ImageManager import ImageManager
# import base64
