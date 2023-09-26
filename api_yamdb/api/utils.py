from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status
from random import choice
from string import ascii_letters


def get_confirmation_code():
    return ''.join(choice(ascii_letters) for i in range(12))

def send_confirmation_code(email, code):
    subject = 'Your Confirmation Code'
    message = f'Your confirmation code is: {code}'
    from_email = 'from@example.com'
    # This should come from environment variables
    send_mail(subject, message, from_email, [email], fail_silently=False)

