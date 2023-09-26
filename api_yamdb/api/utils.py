from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status





def send_confirmation_code(email, code):
    subject = 'Your Confirmation Code'
    message = f'Your confirmation code is: {code}'
    from_email = 'from@example.com'
    # This should come from environment variables
    send_mail(subject, message, from_email, [email], fail_silently=False)

