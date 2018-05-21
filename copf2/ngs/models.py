from django.db import models
from django.contrib import admin
from django.forms import ModelForm
from django import forms
import uuid
import os
from django.core.exceptions import ValidationError
from django.forms.models import inlineformset_factory
from django.forms import widgets
from django.forms import TextInput
from django.forms import DateInput
import pandas as pd
import requests
import json
import glob
import sys
#sys.path.append('/home/debian/copf2/copf2/extra_files')
sys.path.append('extra_files')
import global_vars as g
import secret as ts
from copf_functions import fsk3api, read_json

########################################################################################################################
########################################################################################################################
## MODEL: SCIENTIST
########################################################################################################################
########################################################################################################################

class Scientist(models.Model):
    name = models.CharField(max_length=200,primary_key=True)

###############

    def __unicode__(self):
        return self.name

########################################################################################################################
########################################################################################################################
## MODEL: FLOWLANE
## class methods:
## --create_or_update - return nothing, save self
## object methods:
## --getBarcode - return nothing, save self
## --getStorage - return nothing, save self
## static methods:
########################################################################################################################
########################################################################################################################

class Flowlane(models.Model):
    Single_read = 'SR'
    Paired_read = 'PR'
    READ_TYPE_CHOICES = (
                         (Single_read, 'Single'),
                         (Paired_read, 'Paired'),
                         )
    barcode = models.CharField(max_length=1000,null=True)
    mdsum = models.CharField(max_length=200,null=True)
    name = models.CharField(max_length=200,primary_key=True)
    read_length = models.IntegerField()
    read_type = models.CharField(max_length=2,choices=READ_TYPE_CHOICES)
    results = models.CharField(max_length=20)
    storage = models.CharField(max_length=200,null=True)

###############

    def getBarcodeStrings(self):
        samples = self.sample_set.all()
        b=list()
        for i in samples:
            b.append(str(i.sample_id)+":"+Sample.objects.get(sample_id=i.sample_id).barcode)
        barcodestring=",".join(b)
        self.barcode=barcodestring
        self.save()

###############

    def getStorage(self,path):
        files=glob.glob(path+'/*.bam')
        id=str(self.pk)
        f_list=list()
        for f in files:
            if id in f: # match
                base=os.path.basename(f)
                if self.storage and self.storage != base:
                    print flowlane.name
                    raise Exception("More than one multiplex file!!")
                else:
                    self.storage=base
                    self.save()

###############

    @classmethod
    def create_or_update(cls,mdsum,name,read_length,read_type,results,start):
        obj, created = Flowlane.objects.get_or_create(mdsum=mdsum,name = name,read_length=read_length,read_type=read_type,results=results)
        obj.save()
        start.flowlane.add(obj)
        obj.getBarcodeStrings()
        obj.getStorage(g.my_multiplex)
        obj.save()

########################################################################################################################
########################################################################################################################
## Model: SAMPLE
## class methods:
## --create_or_update - return nothing, calls functions save self
## object methods:
## --tissue_clean - return nothing, save self
## --update_sample_forskalle - return nothing, save self
## --get_flowlanes - return nothing, call flowlane.create_or_update which saves flowlane
## --updateInfo - return nothing, save self
## --checkUpdates - return updates need (dict)
## --correctcopf2 - return nothing, save self
## --correctforskalle - return nothing
## static methods:
## --check_barcode_type - return barcode
########################################################################################################################
########################################################################################################################

class Sample(models.Model):
    
    ORGANISM_CHOICES = (
                        ('Arabidopsis thaliana','Arabidopsis thaliana'),
                        ('Marchantia polymorpha','Marchantia polymorpha'),
                        ('Hornwort','Hornwort'),
                        ('Homo sapiens', 'Homo sapiens'),
                        ('S. pombe','S. pombe'),
                       )
                       
    EXPTYPE_CHOICES = (
                        ('ChIP-Seq', 'ChIP-Seq'),
                        ('Hi-C','Hi-C'),
                        ('MNase-Seq','MNase-Seq'),
                        ('Whole-Genome','Whole-Genome'),
                        ('RNA-Seq','RNA-Seq'),
                        ('ATAC-Seq','ATAC-Seq')
                       )
    STATUS_CHOICES = (
                      ('Ready', 'Ready'),
                      ('Prepared', 'Prepared'),
                      ('Submitted', 'Submitted'),
                      ('Onhold','Onhold'),
                      ('Aborted','Aborted'),
                      )
                       
    antibody = models.CharField(max_length=20)
    barcode = models.CharField(max_length=20,null=True)
    celltype = models.CharField(max_length=20,null=True)
    comments = models.CharField(max_length=200,null=True)
    descr = models.CharField(max_length=200)
    exptype = models.CharField(max_length=20,choices=EXPTYPE_CHOICES)
    genotype = models.CharField(max_length=10)
    organism = models.CharField(max_length=20,choices=ORGANISM_CHOICES)
    preparation_kit = models.CharField(max_length=200,null=True)
    sample_id = models.IntegerField(primary_key=True)
    scientist = models.ForeignKey(Scientist,related_name="related_scientist")
    status = models.CharField(max_length=20,choices=STATUS_CHOICES)
    tissue_type = models.CharField(max_length=20)
    treatment = models.CharField(max_length=200)
    ###
    curated = models.NullBooleanField(default=None)
    ###
    flowlane = models.ManyToManyField("Flowlane",blank=True)
    
  
##############
  
    def tissue_clean(self):
        incornames = pd.read_csv(g.my_tissue_file,sep=";")
        wrong = incornames['Incorrect'].tolist()
        if self.tissue_type=="" or self.tissue_type=="nan": # empty string - change to NA
            self.tissue_type="NA"
            self.correctforskalle(tissue_type=self.tissue_type)
        else:
            while self.tissue_type in wrong:
                for i, row in incornames.iterrows():
                    if self.tissue_type==row['Incorrect']:
                        self.tissue_type=row['Correct']
                        self.correctforskalle(tissue_type=self.tissue_type)
        print "run"
        self.save()

###############
    
    @staticmethod
    def check_barcode_type(barcode,secondary_tag,barcode_type):
        if barcode_type is not None:
            mbc=barcode+secondary_tag
        else:
            mbc=barcode
        return mbc

###############

    def update_sample_forskalle(self,scientist,exptype,mbc,status):
        # if self.exptype != exptype or self.scientist != scientist:
        #    sys.exit(2)
        #if self.status != status:
        #    self.status = status
        #if self.barcode != mbc:
        #    self.barcode = mbc
        #self.get_flowlanes()
        self.tissue_clean()
        #self.getRawfiles(g.my_demultiplex)
        self.save()

###############

    def updateInfo(self,**fields):
        #  updates=self.checkUpdate(**fields)
        #self.curated=True
        #if bool(updates):
        #    self.correctforskalle(**updates)
        #    self.correctcopf2(**updates)
        #    self.tissue_clean()
        self.save()

###############

    def checkUpdate(self,**new_data):
        #zeros= ["None","nan","NaN","na",""]
        #exclude = ["flowlane"]
        #old = self.__dict__
        #updates = {}
        #for a in new_data:
        #   if a not in exclude:
        #       if new_data[a] != old[a]:
        #           if not (old[a] in zeros and pd.isnull(new_data[a])) and not (old[a] in zeros and new_data[a] in zeros):
        #               updates.update({a: new_data[a]})
        #return updates
        return self

###############

    def correctcopf2(self,**corrections):
        #for attr, value in corrections.iteritems():
        #    setattr(self, attr, value)
        self.save()

###############

    def correctforskalle(self,**corrections):
        #passw=ts.passw
        #user='Elin.Axelsson'
        #s = requests.Session()
        #auth = { 'username': user , 'password': passw }
        #r = s.post('http://ngs.csf.ac.at/forskalle/api/login', data=auth)
        #if (r.status_code != 200):
        #    raise Exception('Authentication error?')
        #r = s.get('http://ngs.csf.ac.at/forskalle/api/samples/'+str(self.pk))
        #if (r.status_code != 200):
        #        raise Exception('get error')
        #sample = r.json()
        #for kw in corrections:
        #    if sample[kw] != corrections[kw]:
        #        sample[kw] = corrections[kw]
        #res=s.post('http://ngs.csf.ac.at/forskalle/api/samples/'+str(self.pk), json=sample)
        print corrections
###############

    def getRawfiles(self,path):
        #files=glob.glob(path+'/*.bam')
        #id=str(self.pk)
        #f_list=list()
        #for f in files:
        #    if id in f: # match
        #        base=os.path.basename(f)
        #       obj, created = Rawfile.objects.get_or_create(name=base,sample=self)
        self.save()

###############

    def get_flowlanes(self):
        #  if not self.status=="Ready": ## sample results not finished
        return None
        #forskalleapi('runs/sample/'+str(self.sample_id),'temp.json')
        #data = read_json('temp.json')
        #nr = len(data) ## number of flowcell+lane the sample is on
        #for i in range(0,nr): ## process each flowcell+lane at the time
        #   myd = data[i]
        #   name = myd['flowcell_id']+"_"+str(myd['num'])
        #   read_length = myd['flowcell']['readlen']
        #   if myd['flowcell']['paired']==1:
        #       read_type="PR"
        #   else:
        #       read_type="SR"
        #   results = myd['is_ok']
        #   if results==1:
        #       cc = myd['unsplit_checks'] # md5 sum for multiplexed bam file
        #       if not len(cc)==1:
        #           raise Exception("wrong number of raw checks "+str(sample.sample_id)+" "+str(len(cc)))
        #       for i in cc:
        #           mdsum = cc[i]['md5']
        #   else:
        #       mdsum = None
        #   if Flowlane.objects.filter(pk=name).exists():
        #       ex=Flowlane.objects.get(pk=name)
        #       if ex.mdsum != mdsum:
        #           if ex.mdsum is None:
        #               print "mdsum has been provided"
        #               ex.mdsum = mdsum
        #               ex.save()
        #           else:
        #               print "wrong mdsum"
        #               print ex.mdsum
        #               print mdsum
        #               sys.exit(2)
        #       if ex.read_length != read_length:
        #           print "wrong read_length"
        #           sys.exit(2)
        #       if ex.read_type != read_type:
        #           print "wrong read_type"
        #           sys.exit(2)
        #       if int(ex.results) is not int(results):
        #           if int(ex.results) == 0:
        #               print "results are in"
        #               ex.results = results
        #               ex.save()
        #           else:
        #               print "wrong results"
        #               print int(results)
        #               print int(ex.results)
        #               sys.exit(2)
        #   Flowlane.create_or_update(mdsum,name,read_length,read_type,results,self)
        #os.remove('temp.json') # remove temp file to avoid getting samples mixed up

###############

    @classmethod
    def create_or_update(cls,antibody,barcode,celltype,comments,descr,exptype,genotype,organism,preparation_kit,sample_id,scientist,secondary_tag,status,tissue_type,treatment,barcode_type):
        mbc = Sample.check_barcode_type(barcode,secondary_tag,barcode_type)
        if not Sample.objects.filter(pk=sample_id).exists(): #create and SAVE new sample
            object = cls(antibody = antibody, barcode = mbc, celltype = celltype, comments = comments, descr = descr, exptype=exptype,genotype = genotype, organism = organism, preparation_kit = preparation_kit,sample_id = sample_id, scientist = scientist,status = status,tissue_type=tissue_type,treatment=treatment)
            object.save()
        else:
            object = Sample.objects.get(pk=sample_id)
        ## if nothing has changed stop ... flowlane is problem
        object.update_sample_forskalle(scientist,exptype,mbc,status)



########################################################################################################################
########################################################################################################################
## MODEL: RAWFILE
########################################################################################################################
########################################################################################################################

class Rawfile(models.Model):
    name = models.CharField(max_length=200,null=True)
    sample = models.ForeignKey(Sample,related_name="related_sample")

###############

    def __unicode__(self):
        return unicode(self.name)

