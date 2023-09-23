import django_filters
from django.core.mail import send_mail
from reviews.models import Title
from rest_framework.response import Response
from rest_framework import status


class TitleFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(field_name='genre__slug')
    category = django_filters.CharFilter(field_name='category__slug')
    year = django_filters.NumberFilter(field_name='year')
    name = django_filters.CharFilter(field_name='name')

    class Meta:
        model = Title
        fields = ['genre', 'category', 'year', 'name']


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
