import sys, getopt
import os
import requests
import json


from django.core.wsgi import get_wsgi_application
os.environ['DJANGO_SETTINGS_MODULE'] = 'copf2.settings'
application = get_wsgi_application()
from ngs.models import Sample, Scientist, Flowlane, Rawfile
from copf_functions import forskalleapi, read_json, correctforskalle

#####################################################################
####
#####################################################################

if __name__ == '__main__':
    print "start"
    #data=read_json("group_1_years.json")
    #for d in data:
    #   sci, created = Scientist.objects.get_or_create(name = d['scientist'])
#   new_sample = Sample.create_or_update(antibody=d['antibody'],barcode=d['tag'],celltype=d['celltype'],comments=d['comments'],descr=d['descr'],exptype=d['exptype'],genotype=d['genotype'],organism=d['organism'],preparation_kit=d['preparation_kit'],sample_id=d['id'],scientist=sci,secondary_tag=d['secondary_tag'],status=d['status'],tissue_type=d['tissue_type'],treatment=d['treatment'])
        
#clean_sample = Sample.correct()

#sa = Sample.objects.all()
#    print "number of samples: " + str(len(sa))
#time = "2+months"
    #gjson="group_"+time.replace('+','_')+".json"
    #forskalleapi('samples?group=Berger&since='+time,gjson)
    #forskalleapi('samples/46948',gjson)
    correctforskalle(46948,tissue_type="Seedlings 12 days old")