import os

from dotenv import load_dotenv
from django.core.mail import send_mail
from random import choice
from string import ascii_letters

load_dotenv()


def get_confirmation_code():
    return ''.join(choice(ascii_letters) for i in range(12))


def send_confirmation_code(email, code):
    subject = 'Your Confirmation Code'
    message = f'Your confirmation code is: {code}'
    from_email = os.getenv('FROM_EMAIL')
    send_mail(subject, message, from_email, [email], fail_silently=False)
