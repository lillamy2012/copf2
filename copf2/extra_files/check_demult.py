import os
import re
import glob
import ntpath


def getBamFiles(path): # get all bam files in folder
    bamFiles=glob.glob(path+'/*.bam')
    return(bamFiles)

#def checkIfThere(path,sampleL):
#   files=getBamFiles(path)
#   FL=getDBList(sampleL)
#   for f in FL:
#       hit=0
#       for s in files:
#           if f in s:
#               hit=hit+1

def checkIfThere(files,sample): # given a sample and a list of files check if file for sample exist
    hit=0
    f_list=list()
    for f in files:
        if sample in f:
            hit=hit+1
            f_list.append(f)
    if hit > 0:
        return(f_list)


def getDBList(FL):
    dbList=list()
    for i in FL:
        if len(i.flowlane.all()) > 0:
            dbList.append(str(i.pk))
    return(dbList)



bampath="/Users/elin.axelsson/berger_group/lab/Raw/demultiplexed/"

if __name__ == '__main__':
    from django.core.wsgi import get_wsgi_application
    os.environ['DJANGO_SETTINGS_MODULE'] = 'copf2.settings'
    application = get_wsgi_application()
    from ngs.models import Sample, Scientist, Flowlane

    all_samples=getDBList(Sample.objects.all())
    all_files = getBamFiles(bampath)
    for i in all_samples:
        res=checkIfThere(all_files,i)
        print(res)

#checkIfThere(bampath,all)
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
                        
                        
                
                        

