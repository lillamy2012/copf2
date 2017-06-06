import os
import re
import glob
import ntpath


def getBamFiles(path):
    bamFiles=glob.glob(path+'/*.bam')
    #bamList=list()
    #for i in bamFiles:
    #   bamList.append(ntpath.basename(i)[0:11])
    return(bamFiles)

def checkIfThere(path,sampleL):
    files=getBamFiles(path)
    FL=getDBList(sampleL)
    for f in FL:
        print f
        print "***"
        print [s for s in files if f in s]


def getDBList(FL):
    dbList=list()
    for i in FL:
        dbList.append(str(i.pk))
    return(dbList)

def compare(FL,path):
    bamList=getBamFiles(path)
    dbList=getDBList(FL)
    db_uniq=list(set(dbList) - set(bamList))
    bam_uniq=list(set(bamList) - set(dbList))
    common = list(set(bamList).intersection(dbList))
    res= {'db_unique':db_uniq, 'bam_unique':bam_uniq, 'common':common}
    return(res)

bampath="/Users/elin.axelsson/berger_group/lab/Raw/demultiplexed/"

if __name__ == '__main__':
    from django.core.wsgi import get_wsgi_application
    os.environ['DJANGO_SETTINGS_MODULE'] = 'copf2.settings'
    application = get_wsgi_application()
    from ngs.models import Sample, Scientist, Flowlane

    all=Sample.objects.all()
    checkIfThere(bampath,all)
    #okay=Flowlane.objects.filter(results=1)
    #not_okay=Flowlane.objects.filter(results=0)
    #compALL = compare(all,bampath)
#compOKAY = compare(okay,bampath)
    #compNOT = compare(not_okay,bampath)
    
    ## Critical part: any okay bam files missing?
    #if len(compOKAY['db_unique'])>0:
    #   print "***************************"
    #   print "WARNING!!! Bam files are missing! The following flowcells + lanes are not downloaded although the #quality was deemed good:"
    #for i in compOKAY['db_unique']:
    #       print i
    #   print "***************************"

    ## Less critical bam file exist but no database record
    #if len(compALL['bam_unique'])>0:
    #   print "***************************"
    #   print "WARNING!!! Bam files exists that are not recorded in the database. This may not be a critical problem #but please check that the database is correct and that the following bam files are rightly left out:"
    #for i in compALL['bam_unique']:
    #       print i
    #    print "***************************"

    ## For information only - bam files with low quality
    #if len(compNOT['common'])>0:
    #   print "***************************"
    #   print "FYI - according to the database records the following bam files have too low quality to be used:"
    ##       print i
    #  print "***************************"

    ## Now raise error if bam files are missing
    #if len(compOKAY['db_unique'])>0:
    #   raise Exception("Bam files are missing - please investige, correct and re-run this script")
    #else:
#   print "Check run successfully, please check warnings for uncritical inconsistencies"
                        
                        
                
                        

