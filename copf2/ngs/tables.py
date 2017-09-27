from __future__ import division
import django_tables2 as tables
from ngs.models import Scientist, Sample, Flowlane, Rawfile
from django_tables2.utils import A  # alias for Accessor
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django_tables2 import SingleTableView


class ScientistTable(tables.Table):
    class Meta:
        model = Scientist
        attrs = {"class": "paleblue"}

    name= tables.LinkColumn('samples', text='A(name)')
    num = tables.Column(empty_values=(),verbose_name="# Samples",orderable=False)
    curated= tables.Column(empty_values=(),verbose_name="# Curated",orderable=False)
    
    def render_curated(self,record):
        cur = len(Sample.objects.filter(scientist=record.name).filter(curated=True))
        return cur
    
    def order_curated(self, queryset, is_descending):
        name = getattr(self.data, 'model')
        queryset = queryset.annotate(
            length=len(Sample.objects.filter(scientist=name).filter(curated=True))
        ).order_by(('-' if is_descending else '') + 'length')
        return (queryset, True)
    
    def render_num(self,record):
        nrsamples = len(Sample.objects.filter(scientist=record.name))
        return nrsamples

    def render_name(self, record):
        cur = len(Sample.objects.filter(scientist=record.name).filter(curated=True))
        rew = len(Sample.objects.filter(scientist=record.name).filter(review=True))
        
        if rew>0:
            proc = cur/rew
        else:
            proc = 0
        url = reverse('samples')
        if proc > 0.95:
            return format_html('<span class="glyphicon glyphicon-star" style="color:gold" ></span> <a href="{}?scientist={}">{}</a>', url, record.name ,  record.name)
        elif proc > 0.5:
            return format_html('<span class="glyphicon glyphicon-star-empty" style="color:gold" ></span> <a href="{}?scientist={}">{}</a>', url, record.name ,  record.name)
        else:
            return format_html('<a href="{}?scientist={}">{}</a>', url, record.name ,  record.name)

class SampleTable(tables.Table):
    class Meta:
        model = Sample
        attrs = {"class": "paleblue"}
        exclude = ('review','changed')
        sequence = ('curated','sample_id')
    flow_name = tables.Column(accessor="flowlane", verbose_name="Flowlane")
    raw_file = tables.Column(accessor="related_sample",verbose_name="Raw files")
    scientist= tables.LinkColumn('samples', text='A(scientist)')
    seqtype = tables.Column(accessor="flowlane", verbose_name="Seq.Type")
    
    def render_seqtype(self, value, table):
        if value is not None:
            seqList = list(value.all())
            tot = ""
            for s in seqList:
                pair = s.read_type + str(s.read_length) + ','
                tot += pair
            return tot[:-1]
        return '-'
    
    
    def render_curated(self, value):
        if value is True:
            return format_html('<span class="glyphicon glyphicon-ok-circle" style="font-size:150%;color:rgb(112, 244, 161)" ></#span>')
        else:
            return format_html('<span class="glyphicon glyphicon-remove-circle" style="font-size:150%;color:pink" ></span>')


    def render_flow_name(self, value ):
        if value is not None:
            return ', '.join([flowlane.name for flowlane in value.all()])
        return '-'

    def render_scientist(self, record):
        url = reverse('samples')
        return format_html('<a href="{}?scientist={}">{}</a>', url, record.scientist ,  record.scientist)

    def render_raw_file(self , value, table):
        if value is not None:
            fileList = list(value.all())
            files = ""
            uFirst = True
            for u in fileList:
                if not uFirst:
                    files += ", "
                else:
                    uFirst = False
                files += u.name
            return files
        return '-'

        #return ', '.join([raw_file.name for rawfile in value.all()])
#

class SampleList(SingleTableView):
    model = Sample
    table_class = SampleTable


class FlowlaneTable(tables.Table):
    class Meta:
        model = Flowlane
        attrs = {"class": "paleblue"}
        sequence = ('name', 'results','read_type','read_length','storage','mdsum', 'barcode')

    name = tables.LinkColumn('samples', text='A(name)')

    def render_name(self, record):
        url = reverse('samples')
        return format_html('<a href="{}?flowlane={}">{}</a>', url, record.name ,  record.name)
