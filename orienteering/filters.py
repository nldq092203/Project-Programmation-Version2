import django_filters
from . import models

class GroupRunnerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    department = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = models.GroupRunner
        fields = ['name', 'department']

class EventFilter(django_filters.FilterSet):
    is_finished = django_filters.CharFilter(lookup_expr='icontains')
    department = django_filters.CharFilter(lookup_expr='icontains')
    group_runner__name = django_filters.CharFilter(lookup_expr='icontains')
    publish = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = models.Event
        fields = ['is_finished', 'department', 'group_runner__name', 'publish']