from flask import Blueprint, jsonify, request, g
from utils.FBQueries import FBQueries, firebase_auth_required
from utils.helpers import set_err_args, assign_res, generate_chat_id

chat = Blueprint('chat', __name__)

# Handles Any route from the frontend that starts with: `/api/v1/chat`
# Routes for sending, retieving chats. Anything solely chat related.

@chat.route('/', methods=['POST'])
@firebase_auth_required
def send_chat():
    try: 
        current_user_id = g.current_user['uid']
        receiver_id = request.json.get('receiverId')
        message = request.json.get('message')

        if not receiver_id: raise Exception('Unable to text this user.', 400)
        if current_user_id == receiver_id: raise Exception('You are trying to send a message to yourself.', 400)
        if not message: raise Exception('Message is empty.')


        receiver = FBQueries.get_user(receiver_id)
        if receiver is None: raise Exception('No user was found with this identity.', 404)

        my_last_chats = FBQueries().get_last_chats(current_user_id)
        last_chat_with_other_user = [chat for chat in my_last_chats if chat['sender_id'] == receiver_id or chat['receiver_id'] == receiver_id] if len(my_last_chats) else None
        last_chat = last_chat_with_other_user[0] if last_chat_with_other_user and len(last_chat_with_other_user) else None

        if last_chat: FBQueries().update_chat(last_chat['id'], {'is_last_chat': False})
        new_chat = FBQueries().new_chat(sender_id=current_user_id, receiver_id=receiver_id, message=message)

        return jsonify({**assign_res(), "newChat": new_chat})
    except Exception as err:
        print(err)
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code

@chat.route('/', methods=['GET'])
@firebase_auth_required
def get_recent_chats():
    try:
        current_user_id = g.current_user['uid']
        last_chats = [chat for chat in FBQueries().get_last_chats(current_user_id)]
        return jsonify({**assign_res(), "chats": last_chats, "results": len(last_chats)})
    except Exception as err:
        print(err)
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code
    

@chat.route('/<other_user_id>', methods=['GET'])
@firebase_auth_required
def get_chats_with(other_user_id):
    try:
        other_user_id
        chats = FBQueries.get_chats(other_user_id)
        other_user = FBQueries.get_user(other_user_id)

        return jsonify({**assign_res(), "chats": chats, "other_user": other_user, "results": len(chats)})
    except Exception as err:
        print(err)
        err_message, err_code = set_err_args(err.args)
        return jsonify({**assign_res('error'), 'message': err_message}), err_code

# @chat.route('/<chat_id>', methods=['DELETE'])
# @login_required
# def delete_chat(chat_id):
#     try:
#         chat_id = int(chat_id)
#         chat = Chat.query.get(chat_id)
#         if not chat: raise Exception('Chat not found', 404)

#         if chat.is_last_chat:
#             other_user_id = chat.sender_id if current_user.id == chat.receiver_id else chat.receiver_id
#             prev_chat = Chat.query.filter(and_(
#             or_(Chat.sender_id == current_user.id, Chat.sender_id == other_user_id),
#             or_(Chat.receiver_id == current_user.id, Chat.receiver_id == other_user_id))).order_by(desc(Chat.id)).offset(1).first()

#             if prev_chat: prev_chat.is_last_chat = True


#         db.session.delete(chat)
#         db.session.commit()

#         return jsonify({**assign_res(), "message": "Deleted Successfully"})
#     except Exception as err:
#         err_message, err_code = set_err_args(err.args)
#         return jsonify({**assign_res('error'), 'message': err_message}), err_code