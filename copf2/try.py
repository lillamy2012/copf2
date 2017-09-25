from pop_func import *

import sys, getopt
import os
import requests
import json
import glob

##################################################
### help functions
##################################################

### functions for reading json and query forskalle and to get files from path



#################################################


if __name__ == '__main__':

#time = inarg(sys.argv[1:])
    time = "3+months"
    gjson="group_"+time.replace('+','_')+".json"
    print gjson
    print "Starting second generation population script..."
    from django.core.wsgi import get_wsgi_application
    os.environ['DJANGO_SETTINGS_MODULE'] = 'copf2.settings'
    application = get_wsgi_application()
    from ngs.models import Sample, Scientist, Flowlane, Rawfile
    
    #sa =Sample.objects.get(pk=52521)
    #print sa.flowlane.all()
    
    
    ## start
    print "samples from forskalle"
    forkalleapi('samples?group=Berger&since='+time,gjson)

    data=read_json(gjson)
    for d in data:
        print d['id']
        print d['status']
        sci=add_scientist(name=d['scientist'])
        print "ok"
        sam=create_or_update_core_sample(sample_id=d['id'],scientist=sci,exptype=d['exptype'],barcode=d['barcode'],status=d['status'],secondary_tag=d['secondary_tag'])
##(could also take instance instead of id)
#print sam.status
        sam= add_or_update_user_info_sample(sample_id=d['id'],antibody=d['antibody'],celltype=d['celltype'],comments=d['comments'],descr=d['descr'],genotype=d['genotype'].rstrip(),organism=d['organism'],preparation_kit=d['preparation_kit'],tissue_type=d['tissue_type'],treatment=d['treatment'])
        print sam.status
        ExtractAndAdd_flowlane(sam)


    fl = Flowlane.objects.all()
    sa = Sample.objects.all()
    rf = Rawfile.objects.all()
    print "number of flowlanes: " + str(len(fl))
    for i in fl:
        print i.name, i.barcode
        print "number of samples: " + str(len(sa))
        print "number of files: " + str(len(rf))
