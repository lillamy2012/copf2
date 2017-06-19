import sys, getopt
import os
import requests
import json
import glob

##################################################
### help functions
##################################################

### functions for reading json and query forskalle and to get files from path

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

def getBamFiles(path): # get all bam files in folder
    bamFiles=glob.glob(path+'/*.bam')
    return(bamFiles)

### function to check if status has changed and than update:

def check_and_update_sample_status(sample_id,status):
    ex=Sample.objects.get(pk=sample_id)
    if ex.status != status:
        print "status has changed"
        ex.status = status
        ex.save()

### extra function to debug (flowlane)

def check_if_identical(mdsum,name,read_length,read_type,results):
    ex=Flowlane.objects.get(pk=name)
    if ex.mdsum != mdsum:
        print "wrong mdsum"
        print ex.mdsum
        print mdsum
    if ex.read_length != read_length:
        print "wrong read_length"
    if ex.read_type != read_type:
        print "wrong read_type"
    if int(ex.results) is not int(results):
        print "wrong results"
        print int(results)
        print int(ex.results)

### functions for adding entries to db (sample, scientist, flowlane (flowcell+lane) and rawfile)


def add_rawfile(name,sample):
    obj, created = Rawfile.objects.get_or_create(name=name,sample=sample)
    return(obj)

def add_sample(antibody,barcode,celltype,comments,descr,exptype,genotype,organism,preparation_type,sample_id,scientist,status,tissue_type,treatment):
    if Sample.objects.filter(pk=sample_id).exists():
        print sample_id
        check_and_update_sample_status(sample_id,status)
    obj, created = Sample.objects.get_or_create(antibody=antibody,barcode=barcode,celltype=celltype,comments = comments,descr = descr, exptype=exptype, genotype = genotype, organism = organism, preparation_type = preparation_type,sample_id = sample_id,  scientist = scientist,status=status, tissue_type = tissue_type, treatment = treatment)
    return(obj)

def add_scientist(name):
    obj, created = Scientist.objects.get_or_create(name = name)
    return(obj)

def add_flowlane(mdsum,name,read_length,read_type,results):
    ## check if flowlane exists, if so is it the same
    if Flowlane.objects.filter(pk=name).exists():
        print name
        check_if_identical(mdsum,name,read_length,read_type,results)
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




#####################################################
### main functions
#####################################################

#### function that create rawfiles
def checkIfThere(files,sample,type):
    id=str(sample.pk)
    f_list=list()
    for f in files:
        if id in f:
            base=os.path.basename(f)
            if type == "raw":
                add_rawfile(name=base,sample=sample)
            elif type == "storage":
                add_storage(flowlane=sample,file=base)


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
            for i in cc:
                md5 = cc[i]['md5']
        else:
            md5 = None

        flow=add_flowlane(md5,name,readlen,readtype,results)
        link_sample_flowlane(sample,flow)
    os.remove('temp.json') # remove temp file to avoid getting samples mixed up

### wrapper function for rawfiles

def createRawfileEntries(sampleList,path,type):
    files=getBamFiles(path)
    for sample in sampleList:
        checkIfThere(files,sample,type)

### wrapper function to create scientists, samples and flowlanes from group json

def createEntries(json):
    data=read_json(json)
    for d in data:
        sc=add_scientist(name=d['scientist'])
        if d['secondary_tag'] is not None:
            mbc=d['tag']+d['secondary_tag']
        else:
            mbc=d['tag']
        ns=add_sample(antibody=d['antibody'],barcode=mbc,celltype=d['celltype'],comments=d['comments'],descr=d['descr'],exptype=d['exptype'],genotype=d['genotype'].rstrip(),organism=d['organism'],preparation_type=d['preparation_type'],sample_id=d['id'],scientist=sc,status=d['status'],tissue_type=d['tissue_type'],treatment=d['treatment'])
        mu=extractAndAdd_flowlane(ns)

### wrapper to update barstring for all flowlanes in db

def update_all_flowlanes():
    for i in Flowlane.objects.all():
        getBarcodeStrings(i)

### read in arguments (time to check)

def inarg(argv):
    try:
        opts, args = getopt.getopt(argv,"hd:",["date="])
    except getopt.GetoptError:
        print 'populate.py -d <date>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'populate.py -d <date>'
            sys.exit()
        elif opt in ("-d", "--date"):
            time = arg
    if not 'time' in locals():
        print 'populate.py -d <date>'
        sys.exit(2)
    print 'date is',time
    return(time)

#############################################################
### running the program
#############################################################

#time='99+years'



if __name__ == '__main__':
    
    time = inarg(sys.argv[1:])
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
    #forkalleapi('samples?group=Berger&to=2017-01-01&from=2000-10-01',gjson)
    print "creating sample from json"
    createEntries(gjson)
    print "generating barcode strings"
    update_all_flowlanes()
    ## createRawfiles
    path = "/Users/elin.axelsson/berger_group/lab/Raw/demultiplexed/"
    sampleList=Sample.objects.all()
    createRawfileEntries(sampleList,path,"raw")
    path = "/Users/elin.axelsson/berger_group/lab/Raw/multiplexed/"
    flowList=Flowlane.objects.all()
    createRawfileEntries(flowList,path,"storage")
    fl = Flowlane.objects.all()
    sa = Sample.objects.all()
    rf = Rawfile.objects.all()
    print "number of flowlanes: " + str(len(fl))
    for i in fl:
        print i.name, i.barcode
    print "number of samples: " + str(len(sa))
    print "number of files: " + str(len(rf))

## okat 15352
##16844, 32315
## check problematic sample
