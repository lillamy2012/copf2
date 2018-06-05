import sys
import datetime
#import unittest
from django.test import TestCase
sys.path.append('extra_files')

from copf_functions import fsk3api, read_json, getAPIstring
from ngs.models import Sample, Scientist, Flowlane, Rawfile

# Create your tests here.

class functionsTests(TestCase):
    
    def test_apistring(self):
        self.assertEqual(str(getAPIstring()),"samples/group?filter.group=Berger")
        date=datetime.date.today() + datetime.timedelta(-30)
        self.assertEqual(getAPIstring(days=30),"samples/group?filter.group=Berger&filter.received_after="+str(date))
        with self.assertRaises(Exception):
            getAPIstring(days=-3)

# fsk3api, read_json


class SampleTest(TestCase):
    
    
    def test_sample(self):
        self.assertEqual(Sample.check_barcode_type('AAA','BBB',1),'AAABBB')
        self.assertEqual(Sample.check_barcode_type('AAA','BBB',None),'AAA')
        sci, created = Scientist.objects.get_or_create(name = "Sean Montgomery")
        sam = Sample.create_or_update(antibody="H3K4me3",barcode="CTTGTA",celltype="50000",comments= "null",descr = "NEBNext Ultra II", exptype="ULI-ChIP", genotype="Tak1 WT",organism="Marchantia polymorpha", preparation_kit="",sample_id="66168",scientist=sci,secondary_tag="random",status= "Ready",tissue_type = "Gametophyte 11 day", treatment= "Rep 2",barcode_type= None)
        self.assertEqual(sam.barcode,"CTTGTA")

                                  
                                 
                                 
                                  

### getAPIstring

## works on days right , not if wrong ,default

### fsk3api

## maybe mock?
