from django.shortcuts import render_to_response, render, redirect
from django.http import HttpResponse
from django.db import models
from ngs.models import Sample, Scientist, Flowlane
from ngs.tables import ScientistTable, SampleTable, FlowlaneTable
from ngs.filters import SampleFilter, FlowlaneFilter
from django_tables2 import RequestConfig
from django_tables2.export.export import TableExport

# Create your views here.

def index(request):
    nscient = len(Sample.objects.values_list('scientist').distinct())
    nsamples= len(Sample.objects.values_list('sample_id').distinct())
    nflowlanes = len(Sample.objects.values_list('flowlane').distinct())
    context_dict = {'scientists':nscient,'samples':nsamples, 'flowlanes':nflowlanes }

    return render_to_response('ngs/index.html',context_dict)

def scientists(request):
    table = ScientistTable(Scientist.objects.all())
    RequestConfig(request).configure(table)
    return render(request, 'scientists.html', {'table': table})

def samples(request):
    queryset=Sample.objects.select_related().all()
    data = request.GET.copy()
        #if 'status' not in data:
        # data['status'] = 'Ready'
    f = SampleFilter(data,queryset=queryset)
    table = SampleTable(f.qs)
    RequestConfig(request).configure(table)
    export_format = request.GET.get('_export', None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table)
        return exporter.response('table.{}'.format(export_format))
    
    return render(request, 'samples.html', {'table': table, 'filter':f})

def flowlanes(request):
    queryset=Flowlane.objects.select_related().all()
    data = request.GET.copy()
    f = FlowlaneFilter(data,queryset=queryset)
    table = FlowlaneTable(f.qs)
    data = request.GET.copy()
    RequestConfig(request).configure(table)
    return render(request, 'flowlanes.html', {'table': table, 'filter':f})



#return HttpResponse("Hello, world. You're at the copf2/ngs index.")