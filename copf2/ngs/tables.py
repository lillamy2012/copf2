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
        sequence = ('sample_id','barcode',)


class FlowlaneTable(tables.Table):
    class Meta:
        model = Flowlane
        attrs = {"class": "paleblue"}
        sequence = ('name', 'results','read_type','read_length','storage','mdsum', 'barcode')