import sys, getopt
import os
import requests
import json
sys.path.append('extra_files')

import global_vars as g
import secret as ts

from django.core.wsgi import get_wsgi_application
os.environ['DJANGO_SETTINGS_MODULE'] = 'copf2.settings'
application = get_wsgi_application()
from ngs.models import Sample, Scientist, Flowlane, Rawfile
from copf_functions import forskalleapi, read_json, readin_csv, updateSheet, backupDB

#####################################################################
#### read in arg
#####################################################################

def inarg(argv):
    err='copf2.py -t ["initial","fsupdate","csvupdate",cleanonly"]'
    try:
        opts, args = getopt.getopt(argv,"ht:")
    except getopt.GetoptError:
        print err
        sys.exit(2)
    for opt,arg in opts:
        if opt == '-h':
            print err
            sys.exit()
        elif opt == '-t':
            task = arg
            if arg not in ("initial","fsupdate","csvupdate","cleanonly"):
                print err
                sys.exit(2)
            return task

#####################################################################
#### run main
#####################################################################


if __name__ == '__main__':
    task =inarg(sys.argv[1:])
    print "running in " + task + "-mode"
    forskalle=False
    
    if task == "initial":
        time = "99+months"
        forskalle=True
    
    if task == "fsupdate":
        print "regular update"
        time = "1+months"
        forskalle=True

    if task == "csvupdate":
        print "cleaning update"
        for f in os.listdir(g.my_updatepath):
            print f
            try:
		print "1"
                dd = updateSheet(g.my_updatepath+"/"+f)
		print "2"
                for i in dd:
                    ex = Sample.objects.get(pk=i['sample id'])
                    del i['sample id']
                    ex.updateInfo(**i)
		print "3"
                os.rename(g.my_updatepath+"/"+f, g.my_old+"/"+f)
            except:
                print "error in file "+f

    if task == "cleanonly":
        print "clean only"
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
        os.remove(gjson) # keep dir clean

    if task == "initial":
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



