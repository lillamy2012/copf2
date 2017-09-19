import sys, getopt
import os
import pandas as pd

###########################################
### functions
###########################################

def readin_csv(csv):
    df = pd.read_csv(csv,sep=";")
    keep = df['Sample Id']
    return keep


def inarg(argv):
    try:
        opts, args = getopt.getopt(argv,"hr:c:u:",["review=","curated=","updated"])
    except getopt.GetoptError:
        print 'status.py -rcu[review,curated,uploaded] <csv> - break1'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'status.py -rcu[review,curated,uploaded] <csv> - break2'
            sys.exit()
        elif opt in ("-r", "--review"):
            type = "review"
        elif opt in ("-c", "--curated"):
            type = "curated"
        elif opt in ("-u","--updated"):
            type = "updated"
        file = arg
    if not 'file' in locals() or not 'type' in locals():
        print 'status.py -rcu[review,curated,uploaded] <csv> - break3'
        sys.exit(2)
    print 'type is',type
    return type,file


def UpdateStatus(type,data):
    if type == 'review':
        for d in data:
            up=update_review(d)
    elif type == 'curated':
        for d in data:
            up=update_curated(d)
    elif type == 'updated':
        for d in data:
            up=update_changed(d)
    else:
        print 'wrong type'
        sys.exit(2)

def update_review(id):
    obj, created = State.objects.get_or_create(sample = id)
    obj.review=True
    if obj.curated is None:
        obj.curated=False
    obj.save()

def update_curated(id):
    obj, created = State.objects.get_or_create(sample = id)
    if obj.review != True:
        print 'sample review status was not true! Check why'
        sys.exit(2)
    obj.curated=True
    if obj.changed is None:
        obj.change=False
    obj.save()

def update_changed(id):
    obj, created = State.objects.get_or_create(sample = id)
    if obj.curated != True:
        print 'sample curated status was not true! Check why'
        sys.exit(2)
    obj.changed=True
    obj.save()

##############################
## running
##############################

if __name__ == '__main__':
    from django.core.wsgi import get_wsgi_application
    os.environ['DJANGO_SETTINGS_MODULE'] = 'copf2.settings'
    application = get_wsgi_application()
    from ngs.models import Sample, Scientist, State
    print "start"
    type, file = inarg(sys.argv[1:])
    print type
    samples = readin_csv(file)
    print "ok"
    UpdateStatus(type,samples)


    obj, created = State.objects.get_or_create(sample = 52316)
    print obj.curated






