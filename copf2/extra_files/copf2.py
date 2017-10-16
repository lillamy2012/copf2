import sys, getopt
import os
import requests
import json
import global_vars as g

from django.core.wsgi import get_wsgi_application
os.environ['DJANGO_SETTINGS_MODULE'] = 'copf2.settings'
application = get_wsgi_application()
from ngs.models import Sample, Scientist, Flowlane, Rawfile
from copf_functions import forskalleapi, read_json, readin_csv, updateSheet, backupDB

#####################################################################
####
#####################################################################

if __name__ == '__main__':
    if task is "initial":
        print "init"
        time = "99+months"
        forskalle=True
    if task is "fkupdate":
        print "regular update"
        time = "1+months"
        forskalle=True
    if task is "csvupdate":
        ## for all input files
        dd = updateSheet("input/DJ-14-09-17.csv")
        for i in dd:
            ex = Sample.objects.get(pk=i['sample id'])
            del i['sample id']
            ex.updateInfo(**i)
        ## move sheet to used

    if task is "cleanonly":
        sa = Sample.objects.all()
        for s in sa:
            s.tissue_clean()
            s.save()

    if forskalle:
        gjson="group_"+time.replace('+','_')+".json"
        forskalleapi('samples?group=Berger&since='+time,gjson)
        data=read_json(gjson)
        print "forskalle"
        for d in data:
            sci, created = Scientist.objects.get_or_create(name = d['scientist'])
            new_sample = Sample.create_or_update(antibody=d['antibody'],barcode=d['tag'],celltype=d['celltype'],comments=d['comments'],descr=d['descr'],exptype=d['exptype'],genotype=d['genotype'],organism=d['organism'],preparation_kit=d['preparation_kit'],sample_id=d['id'],scientist=sci,secondary_tag=d['secondary_tag'],status=d['status'],tissue_type=d['tissue_type'],treatment=d['treatment'])

    if task is "initial":
        print "initial backup"
        backupDB(type="initial")
    else:
        print "version backup"
        backupDB(type="versions") 

    print "summary"
    sa = Sample.objects.all()
    print "number of samples: " + str(len(sa))
    fl = Flowlane.objects.all()
    print "number of flowlanes: " + str(len(fl))

