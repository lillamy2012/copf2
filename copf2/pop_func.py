
import sys, getopt
import os
import requests
import json
import glob
import pandas as pd

from django.core.wsgi import get_wsgi_application
os.environ['DJANGO_SETTINGS_MODULE'] = 'copf2.settings'
application = get_wsgi_application()
from ngs.models import Sample, Scientist, Flowlane, Rawfile

#####################################################################
#### help functions
#####################################################################


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

def readin_csv(csv):
    df = pd.read_csv(csv,sep=";")
    keep = df['Sample Id']
    return keep



def linkFiles(path,object,type):
    files=glob.glob(path+'/*.bam')
    id=str(object.pk)
    f_list=list()
    for f in files:
        if id in f:
            base=os.path.basename(f)
            if type == "raw":
                obj, created = Rawfile.objects.get_or_create(name=base,sample=object)
            elif type == "storage":
                obj = Flowlane.objects.get(name=object.name)
                #check if storage exists if so is it the same
                if obj.storage and obj.storage != base:
                    print flowlane.name
                    raise Exception("More than one multiplex file!!")
                else:
                    obj.storage=base
                    obj.save()


def readin_csv(csv):
    df = pd.read_csv(csv,sep=";")
    return(df)

def equal(exist,new):
    zeros= ["None","nan","NaN","na",""]
    if exist != new:
        if (exist in zeros and pd.isnull(new)) or (exist in zeros and new in zeros):
            return True
        else:
            return False
    else:
        return True





######################################################################
#### scientist
######################################################################

###  CREATE scientists
def add_scientist(name):
    obj, created = Scientist.objects.get_or_create(name = name)
    return(obj)

######################################################################
#### rawfile
######################################################################

def add_rawfile(name,sample):
    obj, created = Rawfile.objects.get_or_create(name=name,sample=sample)
    return(obj)


######################################################################
#### flowlane
######################################################################

### function that creates flowlane per sample, using forskalle, links flowcell to sample.should never change!, only results
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
        read_length = myd['flowcell']['readlen']
        if myd['flowcell']['paired']==1:
            read_type="PR"
        else:
            read_type="SR"
        results = myd['is_ok']
        if results==1:
            cc = myd['unsplit_checks'] # md5 sum for multiplexed bam file
            if not len(cc)==1:
                raise Exception("wrong number of raw checks "+str(sample.sample_id)+" "+str(len(cc)))
            for i in cc:
                mdsum = cc[i]['md5']
        else:
            mdsum = None


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
        sample.flowlane.add(obj)
    os.remove('temp.json') # remove temp file to avoid getting samples mixed up


### CREATE barcode strings and add to flowlane (requires that sample - flowcell link is established)
def getBarcodeStrings(flowlane):
    samples = flowlane.sample_set.all()
    b=list()
    for i in samples:
        b.append(str(i.sample_id)+":"+Sample.objects.get(sample_id=i.sample_id).barcode)
    barcodestring=",".join(b)
    flowlane.barcode=barcodestring
    flowlane.save()


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


def update_all_flowlanes():
    for flowlane in Flowlane.objects.all():
        getBarcodeStrings(flowlane)



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
            print "saving status"
            ex.save()
        
        if ex.barcode != mbc:
            print "barcode has changed"
            ex.barcode = mbc
            print "saving barcode"
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
        up=update_state(d,type)

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
        obj.save()

    else:
        print 'wrong type'
        sys.exit(2)


def check_update_sample(row):
    id=row['Sample Id']
    update_state(id,"review")
    cur=False
    obj=Sample.objects.get(pk=id)
    if not equal(obj.antibody,row['Antibody']):
        obj.antibody=row['Antibody']
        obj.save()
        print "update"
        cur=True
    if not equal(obj.celltype,row['Celltype']):
        obj.celltype=row['Celltype']
        obj.save()
        print "update"
        cur=True
    if not equal(obj.comments,row['Comments']):
        obj.comments=row['Comments']
        obj.save()
    if not equal(obj.descr,row['Descr']):
        obj.descr=row['Descr']
        obj.save()
        print "update"
        cur=True
    if not equal(obj.genotype,row['Genotype']):
        obj.genotype=row['Genotype']
        obj.save()
        print "update"
        cur=True
    if not equal(obj.organism,row['Organism']):
        obj.organism=row['Organism']
        obj.save()
        print "update"
        cur=True
    if not equal(obj.tissue_type,row['Tissue Type']):
        obj.tissue_type=row['Tissue Type']
        obj.save()
        print "update"
        cur=True
    if not equal(obj.treatment,row['Treatment']):
        obj.treatment=row['Treatment']
        obj.save()
        print "update"
        cur=True
    if not equal(obj.preparation_kit,row['Library prep']):
        obj.preparation_kit=row['Library prep']
        obj.save()
        print "update"
        cur=True
    if cur:
        update_state(id,"curated")


def clean_tissue(id):
    incornames = pd.read_csv("correct_tissues.csv",sep=";")
    wrong = incornames['Incorrect'].tolist()
    obj = Sample.objects.get(pk=id)
    #print obj.tissue_type
    #print wrong
    #print obj.tissue_type in wrong
    while obj.tissue_type in wrong:
        for i, row in incornames.iterrows():
            if obj.tissue_type==row['Incorrect']:
                obj.tissue_type=row['Correct']
                obj.save()




## in keys else
## upper letter







