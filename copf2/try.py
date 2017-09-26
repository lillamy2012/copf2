from pop_func import forkalleapi, read_json, add_scientist, ExtractAndAdd_flowlane, getBarcodeStrings, update_all_flowlanes, create_or_update_core_sample, add_or_update_user_info_sample, linkFiles

import sys, getopt
import os
import requests
import json
import glob

#################################################

def inarg(argv):
    err='status.py -rcud[review,curated,uploaded,date] <csv>/<json>'
    try:
        opts, args = getopt.getopt(argv,"hr:c:u:d:",["review=","curated=","updated","date="])
    except getopt.GetoptError:
        print err
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print err
            sys.exit()
        elif opt in ("-r", "--review"):
            type = "review"
        elif opt in ("-c", "--curated"):
            type = "curated"
        elif opt in ("-u","--updated"):
            type = "updated"
        elif opt in ("-d","--date"):
            type = "date"
        file = arg
    if not 'file' in locals() or not 'type' in locals():
        print err
        sys.exit(2)
    print 'type is',type
    return type,file


### now create initial from forskalle, time update
#time = inarg(sys.argv[1:])
def initial_and_time(time):
    #time = "3+months"
    #time
    gjson="group_"+time.replace('+','_')+".json"
    print gjson
    print "samples from forskalle"
    forkalleapi('samples?group=Berger&since='+time,gjson)
    data=read_json(gjson)
    for d in data:
        sci=add_scientist(name=d['scientist'])
        sam=create_or_update_core_sample(sample_id=d['id'],scientist=sci,exptype=d['exptype'],barcode=d['tag'],status=d['status'],secondary_tag=d['secondary_tag'])
        sam=add_or_update_user_info_sample(sample_id=d['id'],antibody=d['antibody'],celltype=d['celltype'],comments=d['comments'],descr=d['descr'],genotype=d['genotype'].rstrip(),organism=d['organism'],preparation_kit=d['preparation_kit'],tissue_type=d['tissue_type'],treatment=d['treatment'])
        ExtractAndAdd_flowlane(sam)
    update_all_flowlanes()
    fl = Flowlane.objects.all()
    for flow in fl:
        linkFiles(mu_path,flow,"storage")
    sa = Sample.objects.all()
    for sample in sa:
        linkFiles(de_path,sample,"raw")

#def review_update()


# rf = Rawfile.objects.all()

#   print "number of flowlanes: " + str(len(fl))
#   for i in fl:
#       print i.name, i.barcode
#   print "number of samples: " + str(len(sa))
#   print "number of files: " + str(len(rf))


####

if __name__ == '__main__':
    de_path = "/Users/elin.axelsson/berger_group/lab/Raw/demultiplexed/"
    mu_path = "/Users/elin.axelsson/berger_group/lab/Raw/multiplexed/"
    print "Starting second generation population script..."
    from django.core.wsgi import get_wsgi_application
    os.environ['DJANGO_SETTINGS_MODULE'] = 'copf2.settings'
    application = get_wsgi_application()
    from ngs.models import Sample, Scientist, Flowlane, Rawfile
    type, file = inarg(sys.argv[1:])
    if type=="date":
        initial_and_time(file)



