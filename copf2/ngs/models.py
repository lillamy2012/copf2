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
    #multi_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200,null=True)
    read_length = models.IntegerField(null=True)
    read_type = models.CharField(max_length=2,choices=READ_TYPE_CHOICES,null=True)
    results = models.CharField(max_length=20,null=True)
    storage = models.CharField(max_length=200,null=True)


    def __unicode__(self):
        return unicode(self.name)


################
## Sample
################
class Sample(models.Model):
    #align = models.CharField(max_length=200,null=True)
    antibody = models.CharField(max_length=20)
    barcode = models.CharField(max_length=20,null=True)
    celltype = models.CharField(max_length=20)
    comments = models.CharField(max_length=200)
    descr = models.CharField(max_length=200)
    exptype = models.CharField(max_length=20)
    flowlane = models.ManyToManyField("Flowlane",blank=True, null=True)
    genotype = models.CharField(max_length=10)
    organism = models.CharField(max_length=20)
    preparation_type = models.CharField(max_length=200)
    sample_id = models.IntegerField(primary_key=True)
    scientist = models.ForeignKey(Scientist)
    status = models.CharField(max_length=20)
    tissue_type = models.CharField(max_length=20)
    treatment = models.CharField(max_length=200)
    
    def got_flowlane(self):
        return len(self.flowlane_set.all())

    def __unicode__(self):
        return unicode(self.sample_id)

    def get_fields(self):
        return self._meta.get_all_field_names()

    def get_entry(self,field):
       return self._meta.get_field(field).verbose_name#this will get the field

