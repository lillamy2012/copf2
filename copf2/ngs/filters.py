from ngs.models import Sample,  Scientist, Flowlane
from django import forms
import django_filters
from django_filters import filters
from django_filters.filters import Filter, CharFilter, BooleanFilter, ChoiceFilter, DateFilter, DateTimeFilter, TimeFilter,ModelChoiceFilter,ModelMultipleChoiceFilter, NumberFilter


class SampleFilter(django_filters.FilterSet):
    scientist = django_filters.ModelChoiceFilter(queryset=Scientist.objects.all())
    class Meta:
        model = Sample
        fields = ['exptype','scientist','status','flowlane','organism','sample_id']


class FlowlaneFilter(django_filters.FilterSet):
    class Meta:
        model = Flowlane
        fields = ['name','results']
