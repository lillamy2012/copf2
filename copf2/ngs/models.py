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
from copf_functions import forskalleapi, read_json

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
## object methods:
## --getBarcode
## --getStorage
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
        obj.getStorage("/Users/elin.axelsson/berger_group/lab/Raw/multiplexed/")
        obj.save()

########################################################################################################################
########################################################################################################################
## Model: SAMPLE
## class methods:
## --create_or_update
## object methods:
## --tissue_clean
## --update_sample_forskalle
## --get_flowlanes
## static methods:
## --check_barcode_type
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
    celltype = models.CharField(max_length=20)
    comments = models.CharField(max_length=200)
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
    review = models.BooleanField(default=False)
    curated = models.NullBooleanField(default=None)
    ###
    flowlane = models.ManyToManyField("Flowlane",blank=True)
    
  
##############
  
    def tissue_clean(self):
        incornames = pd.read_csv("extra_files/correct_tissues.csv",sep=";")
        wrong = incornames['Incorrect'].tolist()
        if self.tissue_type=="" or self.tissue_type=="nan": # empty string - change to NA
            self.tissue_type="NA"
        else:
            while self.tissue_type in wrong:
                for i, row in incornames.iterrows():
                    if self.tissue_type==row['Incorrect']:
                        self.tissue_type=row['Correct']
        return(self)

###############
    
    @staticmethod
    def check_barcode_type(barcode,secondary_tag):
        if secondary_tag is not None:
            mbc=barcode+secondary_tag
        else:
            mbc=barcode
        return mbc

###############

    def update_sample_forskalle(self,scientist,exptype,mbc,status):
        if self.exptype != exptype or self.scientist != scientist:
                sys.exit(2)
        if self.status != status:
            self.status = status
        if self.barcode != mbc:
            self.barcode = mbc
        self.get_flowlanes()
        self.tissue_clean()
        self.getRawfiles("/Users/elin.axelsson/berger_group/lab/Raw/demultiplexed/")
        self.save()

###############

    def update_sample_meta(self,antibody,celltype,comments,descr,genotype,organism,preparation_kit,tissue_type,treatment):
        self.antibody=antibody
        self.celltype=celltype
        self.comments=comments
        self.descr=descr
        self.genotype=genotype
        self.organism=organism
        self.preparation_kit=preparation_kit
        self.tissue_type=tissue_type
        self.treatment=treatment
        self.tissue_clean()
        self.save()

###############

    def getRawfiles(self,path):
        files=glob.glob(path+'/*.bam')
        id=str(self.pk)
        f_list=list()
        for f in files:
            if id in f: # match
                base=os.path.basename(f)
                obj, created = Rawfile.objects.get_or_create(name=base,sample=self)

###############

    def get_flowlanes(self):
        if not self.status=="Ready": ## sample results not finished
            #print "sample not ready"
            return None
        #print "query forskalle " + str(self.sample_id)
        forskalleapi('runs/sample/'+str(self.sample_id),'temp.json')
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
            Flowlane.create_or_update(mdsum,name,read_length,read_type,results,self)
        os.remove('temp.json') # remove temp file to avoid getting samples mixed up

###############

    @classmethod
    def create_or_update(cls,antibody,barcode,celltype,comments,descr,exptype,genotype,organism,preparation_kit,sample_id,scientist,secondary_tag,status,tissue_type,treatment):
        mbc = Sample.check_barcode_type(barcode,secondary_tag)
        if not Sample.objects.filter(pk=sample_id).exists(): #create and SAVE new sample
            object = cls(antibody = antibody, barcode = mbc, celltype = celltype, comments = comments, descr = descr, exptype=exptype,genotype = genotype, organism = organism, preparation_kit = preparation_kit,sample_id = sample_id, scientist = scientist,status = status,tissue_type=tissue_type,treatment=treatment)
            object.save()
        else:
            object = Sample.objects.get(pk=sample_id)
        object.update_sample_forskalle(scientist,exptype,mbc,status)


    #    def got_flowlane(self):
#    return len(self.flowlane_set.all())

#   def __unicode__(self):
#       return unicode(self.sample_id)

#   def get_fields(self):
#        return self._meta.get_all_field_names()

#def get_entry(self,field):
#      return self._meta.get_field(field).verbose_name#this will get the field

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

