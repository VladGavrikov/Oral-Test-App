from flask_mail import Message
from app import mail
from flask import render_template
from app import app

import sendgrid
import os
from sendgrid.helpers.mail import *


def send_password_reset_email(user, email):
    token = user.get_reset_password_token()
    sg = sendgrid.SendGridAPIClient(api_key='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')
    from_email = Email("speakfluentapp@gmail.com")
    to_email = email
    subject = "PASSWORD RESET"
    content = render_template('email/reset_password.txt',
                                         user=user, token=token)
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)




def send_email(to, subject, template):
    print("USING API \n")
    sg = sendgrid.SendGridAPIClient(api_key='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')
    from_email = Email("speakfluentapp@gmail.com")
    to_email = to
    subject = subject
    content = template
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)