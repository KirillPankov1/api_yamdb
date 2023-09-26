from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status





def send_confirmation_code(email, code):
    subject = 'Your Confirmation Code'
    message = f'Your confirmation code is: {code}'
    from_email = 'from@example.com'
    # This should come from environment variables
    send_mail(subject, message, from_email, [email], fail_silently=False)


def check_user_permission(instance, user):
    """
    Check if the user has permission to update or delete a review.
    Returns True if the user has permission,
    otherwise returns a Response object with a 403 status.
    """
    if instance.author != user and not \
            user.is_staff and user.role != 'moderator':
        return Response(status=status.HTTP_403_FORBIDDEN)
    return True
