import django_tables2 as tables
from ngs.models import Scientist, Sample, Flowlane
from django_tables2.utils import A  # alias for Accessor
from django.core.urlresolvers import reverse
from django.utils.html import format_html

class ScientistTable(tables.Table):
    class Meta:
        model = Scientist
        attrs = {"class": "paleblue"}

    name= tables.LinkColumn('samples', text='A(name)')

    def render_name(self, record):
        url = reverse('samples')
        return format_html('<a href="{}?scientist={}">{}</a>', url, record.name ,  record.name)

class SampleTable(tables.Table):
    class Meta:
        model = Sample
        attrs = {"class": "paleblue"}
        sequence = ('sample_id','barcode','flow_name')

    flow_name = tables.Column(accessor="flowlane", verbose_name="Flowlane")
    scientist= tables.LinkColumn('samples', text='A(scientist)')
    
    def render_flow_name(self, value):
        if value is not None:
            return ', '.join([flowlane.name for flowlane in value.all()])
        return '-'

    def render_scientist(self, record):
        url = reverse('samples')
        return format_html('<a href="{}?scientist={}">{}</a>', url, record.scientist ,  record.scientist)

class FlowlaneTable(tables.Table):
    class Meta:
        model = Flowlane
        attrs = {"class": "paleblue"}
        sequence = ('name', 'results','read_type','read_length','storage','mdsum', 'barcode')

    name = tables.LinkColumn('samples', text='A(name)')

    def render_name(self, record):
        url = reverse('samples')
        return format_html('<a href="{}?flowlane={}">{}</a>', url, record.name ,  record.name)
