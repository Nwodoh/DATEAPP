from flask import Blueprint, jsonify, session, request 
from flask_login import login_user, logout_user, login_required
from email_validator import validate_email, EmailNotValidError
from utils.helpers import generate_otp, assign_res, set_time_from_now, set_err_args, is_future_date
from utils.EmailManager import EmailManager
from app import db
from models.User import User
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

otp_type_list = ['signup', 'reset_password']
@auth.route('/otp/<otp_type>', methods=['GET'])
def get_otp(otp_type):
    try:
        email = request.json.get('email')
        if not email: raise EmailNotValidError()
        valid = validate_email(email)
        email = valid.email
        if not (otp_type in otp_type_list): return jsonify({**assign_res('error'), "message": "Invalid otp URL"}), 400
        otp = generate_otp()
        expires_at = set_time_from_now()
        otp_str = f'{otp_type}_{email}_otp'
        session[otp_str] = (otp, expires_at)
        print(otp, expires_at)
        user = User.query.filter_by(email = email).first()
        mail =  EmailManager(email_to=email, payload=otp, user=user)
        if otp_type == otp_type_list[0]: 
            if user: raise Exception(f'Email already exists in out database.', 400)
            mail.send_signup_otp()
        if otp_type == otp_type_list[1]: 
            if not user: raise Exception(f'User with email {email} does not exits.', 404)
            mail.send_reset_password_otp()
        return jsonify({**assign_res(), "message": "otp sent", "expiresAt": expires_at})
    except EmailNotValidError:
        return jsonify({**assign_res('error'), 'message': 'Email is Invalid.'}), 400
    except Exception as err:
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code

def verify_otp(otp_type='signup'):
    if not (otp_type in otp_type_list): raise Exception('Invalid otp URL')
    user_otp = request.json.get('otp')
    if not user_otp: raise Exception('Invalid OTP', 400)
    email = request.json.get('email')
    if not email: raise EmailNotValidError()
    valid = validate_email(email)
    email = valid.email

    otp_str = f'{otp_type}_{email}_otp'
    otp_tuple = session.get(otp_str)
    print(otp_tuple)
    if not otp_tuple or len(otp_tuple) < 2: raise Exception('OTP not set', 400)
    otp, expires_at = otp_tuple
    if not (otp and expires_at): raise Exception('Invalid otp', 400)

    if not is_future_date(expires_at): raise Exception('Token Expired. Please generate a new token')
    if otp != user_otp: raise Exception('Incorrect otp', 400)

    session[otp_str] = None
    return True

@auth.route('/signup', methods=['POST'])
def signup():
    try:        
        email = request.json.get('email')
        valid = validate_email(email)
        email = valid.email
        password = request.json.get('password')
        password_confirm = request.json.get('passwordConfirm')

        if password != password_confirm: raise Exception('Your passwords do not match.', 400)

        verify_otp()
        new_user = User(email = email, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()
        login_user(user=new_user, remember=True) # Changed: params

        return jsonify({**assign_res(), "message": "Signup Successful."})
    except EmailNotValidError:
        return jsonify({**assign_res('error'), 'message': 'Email is Invalid.'}), 400
    except Exception as err:
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code

@auth.route('/login', methods=['POST'])
def login():
    try:        
        email = request.json.get('email')
        valid = validate_email(email)
        email = valid.email
        password = request.json.get('password')

        user = User.query.filter_by(email = email).first()
        
        if not user: raise Exception('Incorrect authentification details. Please check you email or password')
        password_is_correct = check_password_hash(user.password, password)
        if not password_is_correct: raise Exception('Incorrect authentification details. Please check you email or password')

        login_user(user=user, remember=True)
        return jsonify({**assign_res(), 'message': 'Login successfull'})
    except EmailNotValidError:
        return jsonify({**assign_res('error'), 'message': 'Email is Invalid.'}), 400
    except Exception as err:
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code


@auth.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return jsonify({**assign_res(), 'message': 'Logout Successful'})

@auth.route('/reset-password', methods=['GET'])
def reset_password():
    try:
        email = request.json.get('email')
        if not email: raise EmailNotValidError()
        valid = validate_email(email)
        email = valid.email
        password = request.json.get('password')
        password_confirm = request.json.get('passwordConfirm')
        min_pass_len = 4
        max_pass_len = 25

        if len(password) < min_pass_len: raise Exception(f'Your password Cannot be less than {min_pass_len} characters long.', 400)
        if len(password) > max_pass_len: raise Exception(f'Your password Cannot be more than {max_pass_len} characters long.', 400)
        if password != password_confirm: raise Exception('Your passwords do not match.', 400)

        verify_otp('reset_password')
        
        user = User.query.filter_by(email=email).first()
        if not user: raise Exception(f'User with {email} was not found.', 404)
        user.password = generate_password_hash(password, method='pbkdf2:sha256')
        db.session.commit()
        login_user(user=user, remember=True)
        
        return {**assign_res('success'), "message": "Password Reset Successfull."}
    except EmailNotValidError:
        return jsonify({**assign_res('error'), 'message': 'Email is Invalid.'}), 400
    except Exception as err:
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code

@auth.route('/protect', methods=['GET'])
def protect(): return jsonify({**assign_res('error'), "message": "Cannot access this route"}), 401 # Changed: err_code

@auth.route('/test', methods=['GET', 'POST'])
@login_required
def test():
    # changed: Removed logout
    return 'Yup!. Logged in!'