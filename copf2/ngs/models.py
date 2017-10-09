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
#from pop_func import forskalleapi

###############
## Scientist
###############
class Scientist(models.Model):
    name = models.CharField(max_length=200,primary_key=True)

    def __unicode__(self):
        return self.name

####################
## Multiplex
####################
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


    def __unicode__(self):
        return unicode(self.name)


################
## Sample
################
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
    
    
    @staticmethod
    def check_barcode_type(barcode,secondary_tag):
        if secondary_tag is not None:
            mbc=barcode+secondary_tag
        else:
            mbc=barcode
        return mbc

    @staticmethod
    def forskalleapi(what,where): ### taken from forskalle api documentation page
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

    @staticmethod
    def read_json(jsonf):
        with open(jsonf, 'r') as json_file:
            data = json.load(json_file)
        return data



    
#def update_sample_meta(self,antibody,celltype,comments,descr,genotype,organism,preparation_kit,tissue_type,treatment)
#        self.antibody=antibody
#        self.celltype=celltype
#        self.comments=comments
#        self.descr=descr
#        self.genotype=genotype
#        self.organism=organism
#        self.preparation_kit=preparation_kit
#        self.tissue_type=tissue_type
#        self.treatment=treatment
#        self.tissue_clean()
#        self.save()


    def update_sample_forskalle(self,scientist,exptype,mbc,status):
        if self.exptype != exptype or self.scientist != scientist:
            print "wrong exptype and/or scientist"
            print sample_id
            sys.exit(2)
        
        if self.status != status:
            print "status has changed"
            self.status = status
        
        if self.barcode != mbc:
            print "barcode has changed"
            self.barcode = mbc

        self.get_flowlanes()
        self.save()
    
    def get_flowlanes(self):
        if not self.status=="Ready": ## sample results not finished
            print "sample not ready"
            return None
        print "query forskalle " + str(self.sample_id)
        Sample.forskalleapi('runs/sample/'+str(self.sample_id),'temp.json')
        data = Sample.read_json('temp.json')
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
        self.flowlane.add(obj)
        os.remove('temp.json') # remove temp file to avoid getting samples mixed up


    @classmethod
    def create_or_update(cls,antibody,barcode,celltype,comments,descr,exptype,genotype,organism,preparation_kit,sample_id,scientist,secondary_tag,status,tissue_type,treatment):
        mbc = Sample.check_barcode_type(barcode,secondary_tag)
        if Sample.objects.filter(pk=sample_id).exists():
            print "update"
            Sample.objects.get(pk=sample_id).update_sample_forskalle(scientist,exptype,mbc,status)
        else:
            new = cls(antibody = antibody, barcode = mbc, celltype = celltype, comments = comments, descr = descr, exptype=exptype,genotype = genotype, organism = organism, preparation_kit = preparation_kit,sample_id = sample_id, scientist = scientist,status = status,tissue_type=tissue_type,treatment=treatment)
            
            cl = new.tissue_clean()
            cl = cl.get_flowlanes()
            print "new"
            cl.save()

    

    #    def got_flowlane(self):
#    return len(self.flowlane_set.all())

#   def __unicode__(self):
#       return unicode(self.sample_id)

#   def get_fields(self):
#        return self._meta.get_all_field_names()

#def get_entry(self,field):
#      return self._meta.get_field(field).verbose_name#this will get the field


################
## Demultiplex
################
class Rawfile(models.Model):
    name = models.CharField(max_length=200,null=True)
    sample = models.ForeignKey(Sample,related_name="related_sample")

    def __unicode__(self):
        return unicode(self.name)

