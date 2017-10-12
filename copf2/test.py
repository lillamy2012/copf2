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
    time = "99+months"
    #gjson="group_"+time.replace('+','_')+".json"
    #forskalleapi('samples?group=Berger&since='+time,gjson)
    #data=read_json(gjson)
    #for d in data:
    #   sci, created = Scientist.objects.get_or_create(name = d['scientist'])
    #   new_sample = Sample.create_or_update(antibody=d['antibody'],barcode=d['tag'],celltype=d['celltype'],comments=d['comments'],descr=d['descr'],exptype=d['exptype'],genotype=d['genotype'],organism=d['organism'],preparation_kit=d['preparation_kit'],sample_id=d['id'],scientist=sci,secondary_tag=d['secondary_tag'],status=d['status'],tissue_type=d['tissue_type'],treatment=d['treatment'])
    
    sa = Sample.objects.all()
    print "number of samples: " + str(len(sa))

#ex = Sample.objects.get(pk=46948)
#   print ex.descr
#   print ex.tissue_type
#   print ex.comments
#   ex.updateInfo(antibody="",celltype="",comments="",descr="Seedlings 12 days old",genotype="Col jon5 KO",organism="Arabidopsis thaliana",preparation_kit=None,tissue_type="12 days old seedlings",treatment="10 min RT Mnase")

#   xx = Sample.objects.get(pk=46948)
#   print xx.comments
#print dict([uu])
# correctforskalle(46948,**uu)


## check tissue_type retro:
    sa = Sample.objects.all()
    for s in sa:
        s.tissue_clean()
        s.save()