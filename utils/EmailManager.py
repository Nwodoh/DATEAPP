from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import Config

class EmailManager():
    def __init__(self, email_to:any, payload:any=''):
        self.email_to=email_to
        self.payload=payload

    def __repr__(self):
        return f'{self.email_to} {self.payload}'

    def send_mail(self, subject:any="Mail From Date App", html_content:any='Mail Content'):
        message = Mail(
        from_email='devtest2yn@gmail.com',
        to_emails=self.email_to,
        subject=subject,
        html_content=html_content)
    
        sg = SendGridAPIClient(Config.SENDGRID_API_KEY)
        try:
            response = sg.send(message)
            return response
        except Exception as err:
            print(err, 'SEND_GRID')

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