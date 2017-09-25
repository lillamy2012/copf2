
import sys, getopt
import os
import requests
import json
import glob

from django.core.wsgi import get_wsgi_application
os.environ['DJANGO_SETTINGS_MODULE'] = 'copf2.settings'
application = get_wsgi_application()
from ngs.models import Sample, Scientist, Flowlane, Rawfile

def forkalleapi(what,where): ### taken from forskalle api documentation page
    passw='zBLOf2@7'
    user='Elin.Axelsson'
    s = requests.Session()
    auth = { 'username': user , 'password': passw }
    r = s.post('http://ngs.csf.ac.at/forskalle/api/login', data=auth)
    if (r.status_code != 200):
        raise Exception('Authentication error?')
    r = s.get('http://ngs.csf.ac.at/forskalle/api/'+what)
    alljson = r.json()
    with open(where, "w") as outfile:
        json.dump(alljson, outfile)

def read_json(jsonf):
    with open(jsonf, 'r') as json_file:
        data = json.load(json_file)
    return data



######################################################################
#### scientist
######################################################################

###  CREATE scientists
def add_scientist(name):
    obj, created = Scientist.objects.get_or_create(name = name)
    return(obj)


######################################################################
#### flowlane
######################################################################

### function that creates flowlane per sample, using forskalle, links flowcell to sample
def ExtractAndAdd_flowlane(sample):
    if not sample.status=="Ready": ## sample results not finished
        print "sample not ready"
        return None
    print "query forskalle " + str(sample.sample_id)
    forkalleapi('runs/sample/'+str(sample.sample_id),'temp.json')
    data = read_json('temp.json')
    nr = len(data) ## number of flowcell+lane the sample is on
    for i in range(0,nr): ## process each flowcell+lane at the time
        myd = data[i]
        name = myd['flowcell_id']+"_"+str(myd['num'])
        readlen = myd['flowcell']['readlen']
        if myd['flowcell']['paired']==1:
            readtype="PR"
        else:
            readtype="SR"
        results = myd['is_ok']
        if results==1:
            cc = myd['unsplit_checks'] # md5 sum for multiplexed bam file
            if not len(cc)==1:
                raise Exception("wrong number of raw checks "+str(sample.sample_id)+" "+str(len(cc)))
            print cc
            md5 = cc[1]['md5']
            print md5
        else:
            md5 = None
        
        flow=add_flowlane(md5,name,readlen,readtype,results)
        sample.flowlane.add(flowlane)
    os.remove('temp.json') # remove temp file to avoid getting samples mixed up





### CREATE flowlane, should never change!, only results
def add_flowlane(mdsum,name,read_length,read_type,results):
    ## check if flowlane exists, if so is it the same
    if Flowlane.objects.filter(pk=name).exists():
        ex=Flowlane.objects.get(pk=name)
        if ex.mdsum != mdsum:
            if ex.mdsum is None:
                print "mdsum has been provided"
                ex.mdsum = mdsum
                ex.save()
            else:
                print "wrong mdsum"
                print ex.mdsum
                print mdsum
                sys.exit(2)
    
        if ex.read_length != read_length:
            print "wrong read_length"
            sys.exit(2)
    
        if ex.read_type != read_type:
            print "wrong read_type"
            sys.exit(2)
                
        if int(ex.results) is not int(results):
            if int(ex.results) == 0:
                print "results are in"
                ex.results = results
                ex.save()
            else:
                print "wrong results"
                print int(results)
                print int(ex.results)
                sys.exit(2)
    obj, created = Flowlane.objects.get_or_create(mdsum=mdsum,name = name,read_length=read_length,read_type=read_type,results=results)
    return(obj)

### CREATE barcode strings and add to flowlane (requires that sample - flowcell link is established)
def getBarcodeStrings(flowlane):
    samples = flowlane.sample_set.all()
    b=list()
    for i in samples:
        b.append(str(i.sample_id)+":"+Sample.objects.get(sample_id=i.sample_id).barcode)
    bas=",".join(b)
    flowcell.barcode=barcodestring
    flowcell.save()


### function to add file name of multiplex
def add_storage(flowlane,file):
    obj = Flowlane.objects.get(name=flowlane.name)
    #check if storage exists if so is it the same
    if obj.storage and obj.storage != file:
        print flowlane.name
        raise Exception("More than one multiplex file!!")
    else:
        obj.storage=file
        obj.save()



######################################################################
#### sample
## id, scientist, exptype, barcode and status - not form user. Status can change, barcode also on occation.
## antibody, celltype, comments, descr, genotype, organism, preparation_kit, tissue_type, treatment - from user. Can be 'corrected'.
######################################################################

## CREATE OR UPDATE core part of sample - update should NOT trigger state update
def create_or_update_core_sample(sample_id,scientist,exptype,barcode,status,secondary_tag):
    if secondary_tag is not None:
        mbc=barcode+secondary_tag
    else:
        mbc=barcode

    if Sample.objects.filter(pk=sample_id).exists():
        ex=Sample.objects.get(pk=sample_id)
        if ex.exptype != exptype or ex.scientist != scientist:
            print "wrong exptype and/or scientist"
            print sample_id
            sys.exit(2)
        
        if ex.status != status:
            print "status has changed"
            ex.status = status
        
        if ex.barcode != mbc:
            print "barcode has changed"
            ex.barcode = mbc
        
        print "saving"
        ex.save()
        return(ex)
    else:
        obj, created = Sample.objects.get_or_create(barcode=mbc, exptype=exptype, sample_id = sample_id, scientist = scientist,status=status)
        return(obj)


## ADD OR UPDATE user defined info to core - update should be accompanied with state update
def add_or_update_user_info_sample(sample_id,antibody,celltype,comments,descr,genotype,organism,preparation_kit,tissue_type,treatment):
    ex=Sample.objects.get(pk=sample_id)
    ex.antibody=antibody
    ex.celltype=celltype
    ex.comments=comments
    ex.descr=descr
    ex.genotype=genotype
    ex.organism=organism
    ex.preparation_kit=preparation_kit
    ex.tissue_type=tissue_type
    ex.treatment=treatment
    ex.save()
    return(ex)


## UPDATE State from list
def UpdateStatus(type,data):
    for d in data:
        up=update_state(d)

# UPDATE STATE
def update_state(id,type):
    obj, created = Sample.objects.get_or_create(sample_id = id)
    if created == True:
        print 'sample entry does not exist' + id
        sys.exit(2)

    if type == 'review':
        obj.review=True
        if obj.curated is None:
            obj.curated=False
        obj.save()

    elif type ==  'curated':
        if obj.review != True:
            print 'sample review status was not true! Check why'
            sys.exit(2)
        obj.curated=True
        if obj.changed is None:
            obj.change=False
        obj.save()

    elif type == 'updated':
        if obj.curated != True:
            print 'sample curated status was not true! Check why'
            sys.exit(2)
        obj.changed=True
        obj.save()

    else:
        print 'wrong type'
        sys.exit(2)


##############
#Create and time updates

##1, add_scientist
##2, add_sample: create_or_update_core_sample , add_or_update_user_info_sample,
##3, add_flowlane (from sample)
##5, rawfiles (sample), rawfiles flowlane


## data=read_json(json)
## for d in data:
## sci=add_scientist(name=d['scientist'])
## sam=create_or_update_core_sample(sample_id=d['id'],scientist=sci,exptype=d['exptype'],barcode=d['barcode'],status=d['status'],secondary_tag=d['secondary_tag'])
##(could also take instance instead of id) sam = add_or_update_user_info_sample(sample_id=d['id'],antibody=d['antibody'],celltype=d['celltype'],comments=d['comments'],descr=d['descr'],genotype=d['genotype'].rstrip(),organism=d['organism'],
## preparation_kit=d['preparation_kit'],tissue_type=d['tissue_type'],treatment=d['treatment'])
##ExtractAndAdd_flowlane(sam)

##############
# Review update

##1, state

##############
# Curated update

##1, update samples: add_or_update_user_info_sample
##2, update state



