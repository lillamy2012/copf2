from django.shortcuts import render_to_response, render, redirect
from django.http import HttpResponse
from django.db import models
from ngs.models import Sample

# Create your views here.

def index(request):
    nscient = len(Sample.objects.values_list('scientist').distinct())
    nsamples= len(Sample.objects.values_list('sample_id').distinct())
    nflowlanes = len(Sample.objects.values_list('flowlane').distinct())
    context_dict = {'scientists':nscient,'samples':nsamples, 'flowlanes':nflowlanes }

    return render_to_response('ngs/index.html',context_dict)




#return HttpResponse("Hello, world. You're at the copf2/ngs index.")