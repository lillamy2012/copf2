import django_tables2 as tables
from ngs.models import Scientist, Sample, Flowlane

class ScientistTable(tables.Table):
    class Meta:
        model = Scientist
        attrs = {"class": "paleblue"}

class SampleTable(tables.Table):
    class Meta:
        model = Sample
        attrs = {"class": "paleblue"}
        sequence = ('sample_id','barcode','flow_name')

    flow_name = tables.Column(accessor="flowlane", verbose_name="Flowlane")

    def render_flow_name(self, value):
        if value is not None:
            return ', '.join([flowlane.name for flowlane in value.all()])
        return '-'

class FlowlaneTable(tables.Table):
    class Meta:
        model = Flowlane
        attrs = {"class": "paleblue"}
        sequence = ('name', 'results','read_type','read_length','storage','mdsum', 'barcode')