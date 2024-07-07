from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from models.User import User
from config import Config

class EmailManager():
    def __init__(self, email_to:any, user:User=User, payload:any='', name_from:str='John Doe'):
        self.user=user
        self.email_to=email_to
        self.payload=payload
        self.name_from=name_from

    def __repr__(self):
        return f'{self.user} {self.email_to} {self.payload} {self.name_from}'

    def send_mail(self, subject:any="Mail From Date App", html_content:any='Mail Content'):
        message = Mail(
        from_email='devtest2yn@gmail.com',
        to_emails=self.email_to,
        subject=subject,
        html_content=html_content)
    
        sg = SendGridAPIClient(Config.SENDGRID_API_KEY)
        response = sg.send(message)
        return response

    def send_signup_otp(self):
        otp = self.payload
        subject = f'Signup OTP' 
        message = f'Here\'s your {otp}'
        response = self.send_mail(subject, message)
        return response
    
    def send_reset_password_otp(self):
        otp = self.payload
        subject = f'DateMap Reset Password Token {otp}' 
        message = f"Here's your forgot password {otp}"
        response = self.send_mail(subject, message)
        return response