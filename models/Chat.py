from app import db

class Chat(db.Model):
    __tablename__ = 'chats'
    id = db.Column(db.Integer, primary_key = True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(140), nullable=False)
    is_last_chat = db.Column(db.Boolean, nullable=False, default=True)
    timestamp = db.Column(db.DateTime, index=True, default=db.func.now())

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_chats')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_chats')

    def to_dict(self, current_user_id=''):
        other_user = None
        is_sender = False
        if self.sender_id == current_user_id: other_user = self.receiver.to_dict()
        elif self.receiver_id == current_user_id: other_user = self.sender.to_dict()
        if other_user and current_user_id == self.sender_id: is_sender = True

        return {
        'id': self.id,
        'message': self.message,
        'sender': self.sender.to_dict(),
        'receiver': self.receiver.to_dict(),
        "other_user": other_user,
        "is_sender": is_sender,
        "timestamp": self.timestamp
        }

    def __repr__(self):
        return f'Chat sent by {self.sender_id}, at {self.timestamp}, to {self.receiver_id}.\n Message: {self.message} and is last_chat is {self.is_last_chat}'
