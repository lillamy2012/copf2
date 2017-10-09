from pop_func import forkalleapi, read_json, add_scientist, ExtractAndAdd_flowlane, getBarcodeStrings, update_all_flowlanes, create_or_update_core_sample, add_or_update_user_info_sample, linkFiles, readin_csv, UpdateStatus, update_state, check_update_sample, clean_tissue

import sys, getopt
import os
import requests
import json
import glob
import pandas as pd
import numpy as np

#################################################

def inarg(argv):
    err='status.py -rcudt[review,curated,uploaded,date,clean] <csv>/<json>'
    try:
        opts, args = getopt.getopt(argv,"hr:c:u:d:t",["review=","curated=","updated","date=","clean="])
    except getopt.GetoptError:
        print err
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print err
            sys.exit()
        elif opt in ("-t","--clean"):
            type = "clean"
            file = ""
        else:
            if opt in ("-r", "--review"):
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





### create initial from forskalle, time update
def initial_and_time(time):
    #time = "3+months"
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

def review_update(type,file):
    df = readin_csv(file)
    keep = df['Sample Id']
    UpdateStatus(type,keep)


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
    #print "Starting second generation population script..."
    from django.core.wsgi import get_wsgi_application
    os.environ['DJANGO_SETTINGS_MODULE'] = 'copf2.settings'
    application = get_wsgi_application()
    from ngs.models import Sample, Scientist, Flowlane, Rawfile
    type, file = inarg(sys.argv[1:])
    err=0
    if type=="date":
        initial_and_time(file)
    if type=="review":
        review_update(type,file)
    if type=="curated":
        count=0
        change=0
        corrected=0
        data = readin_csv(file)
        if not {'Antibody', 'Celltype', 'Comments', 'Descr','Organism','Tissue Type','Treatment','Library prep','Sample Id'}.issubset(data.columns):
            print 'file is missing column'
            err=err+1
            sys.exit(2)
        for i, row in data.iterrows():
            ch=check_update_sample(row)
            count=count+1
            change=change+ch
            cor=clean_tissue(row['Sample Id'])
            corrected=corrected+cor
        print "nr items:" + str(count)
        print "items changed:" + str(change)
        print "tissue corrected:" + str(corrected)
        if err > 0:
            print "WARNING some files did not work: " +str(err)
    if type=="clean":
        ids = Sample.objects.values_list('pk',flat=True).distinct()
        for i in ids:
            clean_tissue(i)

### left to do : update forskalle, remove changed, backup, interface





