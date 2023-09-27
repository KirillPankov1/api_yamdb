import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(field_name='genre__slug')
    category = django_filters.CharFilter(field_name='category__slug')
    year = django_filters.NumberFilter(field_name='year')
    name = django_filters.CharFilter(field_name='name')

    class Meta:
        model = Title
        fields = ['genre', 'category', 'year', 'name']
