from django.shortcuts import render_to_response, render, redirect
from django.http import HttpResponse
from django.db import models
from ngs.models import Sample, Scientist, Flowlane
from ngs.tables import ScientistTable, SampleTable, FlowlaneTable
from django_tables2 import RequestConfig

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
    flowlane = request.GET.get('flowlane')
    if flowlane == None:
        scientist = request.GET.get('scientist')
        if scientist == None:
            table = SampleTable(Sample.objects.all())
        else:
            table = SampleTable(Sample.objects.filter(scientist=scientist))
    else:
        table = SampleTable(Sample.objects.filter(flowlane=flowlane))

    RequestConfig(request).configure(table)
    return render(request, 'scientists.html', {'table': table})

def flowlanes(request):
    table = FlowlaneTable(Flowlane.objects.all())
    RequestConfig(request).configure(table)
    return render(request, 'scientists.html', {'table': table})



#return HttpResponse("Hello, world. You're at the copf2/ngs index.")