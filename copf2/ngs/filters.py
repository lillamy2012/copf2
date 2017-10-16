from ngs.models import Sample,  Scientist, Flowlane
from django import forms
import django_filters
from django_filters import filters
from django_filters.filters import Filter, CharFilter, BooleanFilter, ChoiceFilter, DateFilter, DateTimeFilter, TimeFilter,ModelChoiceFilter,ModelMultipleChoiceFilter, NumberFilter, MultipleChoiceFilter


class SampleFilter(django_filters.FilterSet):
    scientist = django_filters.ModelMultipleChoiceFilter(queryset=Scientist.objects.all(),widget=forms.CheckboxSelectMultiple)
    status = django_filters.AllValuesMultipleFilter(widget=forms.CheckboxSelectMultiple)
    genotype = django_filters.AllValuesFilter(widget=forms.Select)
    #organism =django_filters.CharFilter(widget=forms.Select)
    tissue_type = django_filters.AllValuesMultipleFilter(widget=forms.CheckboxSelectMultiple)
    class Meta:
        model = Sample
        fields = ['antibody','celltype','exptype','genotype','scientist','sample_id','status','flowlane','organism','tissue_type','treatment']


class FlowlaneFilter(django_filters.FilterSet):
    class Meta:
        model = Flowlane
        fields = ['name','results']
