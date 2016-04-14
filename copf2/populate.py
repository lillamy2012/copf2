import os
import requests
import json

##################################################
### help functions
##################################################

### functions for reading json and query forskalle

def read_json(jsonf):
    with open(jsonf, 'r') as json_file:
        data = json.load(json_file)
    return data


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

### functions for adding entries to db (sample, scientist and flowlane (flowcell+lane)

def add_sample(antibody,barcode,celltype,comments,descr,exptype,genotype,organism,preparation_type,sample_id,scientist,status,tissue_type,treatment):
    obj, created = Sample.objects.get_or_create(antibody=antibody,barcode=barcode,celltype=celltype,comments = comments,descr = descr, exptype=exptype, genotype = genotype, organism = organism, preparation_type = preparation_type,sample_id = sample_id,  scientist = scientist,status=status, tissue_type = tissue_type, treatment = treatment)
    return(obj)

def add_scientist(name):
    obj, created = Scientist.objects.get_or_create(name = name)
    return(obj)

def add_flowlane(mdsum,name,read_length,read_type,results):
    obj, created = Flowlane.objects.get_or_create(mdsum=mdsum,name = name,read_length=read_length,read_type=read_type,results=results)
    return(obj)

### function to link flowlane to sample (many to many)

def link_sample_flowlane(sample,flowlane):
    sample.flowlane.add(flowlane)
    return(sample)

### function to updata flowlane with the barcodestring needed for demultiplexing (only group samples included)

def update_flowlane_barcodes(flowlane,barcodestring):
    obj = Flowlane.objects.filter(name=flowlane.name)  # this is a query set which seems to be needed for the update step
    obj.update(barcode=barcodestring)
    return(obj)



#####################################################
### main functions
#####################################################

#### function to create barcodestring per flowlane and updating the flowlane with this info

def getBarcodeStrings(flowlane):
    samples = flowlane.sample_set.all()
    b=list()
    for i in samples:
        b.append(str(i.sample_id)+":"+Sample.objects.get(sample_id=i.sample_id).barcode)
    bas=",".join(b)
    up = update_flowlane_barcodes(flowlane,bas)
    return(up)


### function that creates flowlane per sample, using forskalle

def extractAndAdd_flowlane(sample):
    if not sample.status=="Ready": ## sample results not finished
        return None
    print "query forskalle " + str(sample.sample_id)
    forkalleapi('runs/sample/'+str(sample.sample_id),'temp.json')
    data = read_json('temp.json')
    nr = len(data) ## number of flowcell+lane the sample is on
    for i in range(0,nr): ## process each flowcell+lane at the time
        myd = data[i]
        if myd['is_ok']==1:
            name = myd['flowcell_id']+"_"+str(myd['num'])
            readlen = myd['flowcell']['readlen']
            if myd['flowcell']['paired']==1:
                readtype="PR"
            else:
                readtype="SR"
            cc = myd['unsplit_checks'] # md5 sum for multiplexed bam file
            if not len(cc)==1:
                raise Exception("wrong number of raw checks "+str(sample.sample_id)+" "+str(len(cc)))
            for i in cc:
                md5 = cc[i]['md5']
                results = cc[i]['result']
                flow=add_flowlane(md5,name,readlen,readtype,results)
                link_sample_flowlane(sample,flow)
    os.remove('temp.json') # remove temp file to avoid getting samples mixed up



### wrapper function to create scientists, samples and flowlanes from group json

def createEntries(json):
    data=read_json(json)
    for d in data:
        sc=add_scientist(name=d['scientist'])
        ns=add_sample(antibody=d['antibody'],barcode=d['tag'],celltype=d['celltype'],comments=d['comments'],descr=d['descr'],exptype=d['exptype'],genotype=d['genotype'].rstrip(),organism=d['organism'],preparation_type=d['preparation_type'],sample_id=d['id'],scientist=sc,status=d['status'],tissue_type=d['tissue_type'],treatment=d['treatment'])
        mu=extractAndAdd_flowlane(ns)

### wrapper to update barstring for all flowlanes in db

def update_all_flowlanes():
    for i in Flowlane.objects.all():
        getBarcodeStrings(i)

#############################################################
### running the program
#############################################################

time='99+years'

gjson="group_"+time.replace('+','_')+".json"

print gjson

if __name__ == '__main__':
    print "Starting second generation population script..."
    from django.core.wsgi import get_wsgi_application
    os.environ['DJANGO_SETTINGS_MODULE'] = 'copf2.settings'
    application = get_wsgi_application()
    from ngs.models import Sample, Scientist, Flowlane
    
    ## start
    print "samples from forskalle"
    #forkalleapi('samples?group=Berger&since='+time,gjson)
    print "creating sample from json"
    #createEntries(gjson)
    print "generating barcode strings"
    #update_all_flowlanes()
    fl = Flowlane.objects.all()
    sa = Sample.objects.all()
    print "number of flowlanes: " + str(len(fl))
    for i in fl:
        print i.name, i.barcode
    print "number of samples: " + str(len(sa))

## okat 15352
##16844
## check problematic sample
sa =Sample.objects.get(pk=32315)
print sa.flowlane.all()