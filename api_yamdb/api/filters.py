import django_filters
from django_filters.rest_framework import FilterSet

from reviews.models import Title


class TitleFilter(FilterSet):
    genre = django_filters.CharFilter(lookup_expr='slug')
    category = django_filters.CharFilter(lookup_expr="slug")
    name = django_filters.CharFilter(lookup_expr="contains")
    year = django_filters.NumberFilter()

    class Meta:
        model = Title
        fields = ['name', 'year', 'genre', 'category']
