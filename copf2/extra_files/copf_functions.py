import requests
import json
import os
import pandas as pd
import numpy as np
import shutil
import sys, getopt
import global_vars as g
import secret as ts
import datetime

def getAPIstring(group="Berger",days=0):
    base="samples"
    string = base+"/group?filter.group="+group
    if int(days) > 0:
        f_date = datetime.date.today() + datetime.timedelta(-days)
        string = string+"&filter.received_after="+str(f_date)
    if int(days) < 0:
        raise Exception('nr days most be positive')
    return string


def fsk3api(what,where): ### taken from forskalle3 api documentation page
    base = 'https://ngs.vbcf.ac.at/forskalle3'
    s = requests.Session()
    passw=ts.passw
    user='Elin.Axelsson'
    auth = { 'username': user , 'password': passw }
    r = s.post(base+'/api/login', data=json.dumps(auth))
    if (r.status_code != 200):
    # Forskalle3 error structure
        err = r.json()['errors'][0]
        print err['code']
        print err['title']+': '+err['detail']
        raise Exception('Authentication error?')
    r = s.get(base+'/api/'+what)
    alljson = r.json()
    with open(where, "w") as outfile:
        json.dump(alljson, outfile)


def read_json(jsonf):
    with open(jsonf, 'r') as json_file:
        data = json.load(json_file)
    return data

#def readin_csv(csv):
    #df = pd.read_csv(csv,sep=";") #,dtype={'Sample Id': np.int64})
    ##df.dropna(how="all", inplace=True)
    #df[['Sample Id']]= df[['Sample Id']].apply(pd.to_numeric,downcast='integer')
    #return(df)

#def updateSheet(sheet):
    #columnsToUse=['Antibody', 'Celltype', 'Genotype','Comments', 'Descr','Organism','Tissue Type','Treatment','Library prep','Sample Id']
    #data = readin_csv(sheet)
    #if not {'Antibody', 'Celltype', 'Comments', 'Genotype','Descr','Organism','Tissue Type','Treatment','Library prep','Sample Id'}.issubset(data.columns):
    # missing = list(set(columnsToUse)-set(data.columns))
    #   print 'file is missing column(s) ' + missing
    #   sys.exit(2)
    
    #data = data[columnsToUse]
    #data.columns = ['antibody', 'celltype', 'genotype','comments', 'descr','organism','tissue_type','treatment','preparation_kit','sample id']
    #dd = data.to_dict(orient='records')
#return(dd)

#def backupDB(type,db="db.sqlite3",path=g.my_backup):
    #if type not in [ "versions","initial"]:
    #    print "wrong type"
    #    sys.exit(2)
    #fullpath = path+"/"+type
    #vs=os.listdir(fullpath)
    #if type == "versions":
    #    name=db+"_"
    #   fname = [s for s in vs if name in s] #
    #   num = [ int(s.split('_')[1]) for s in fname ]
    #   Z = [ x for _,x in sorted(zip(num,fname))]
    #   Y = sorted(num)
    #   for i in range(len(Y)-1,-1,-1): # rename all existing except current
    #       shutil.copy2(fullpath+"/"+Z[i],fullpath+"/"+name+str(Y[i]+1))
    #       print fullpath+"/"+Z[i]+","+fullpath+"/"+name+str(Y[i]+1)
    #
    #   shutil.copy2(fullpath+"/"+db,fullpath+"/"+db+"_1") # rename current
    #   print fullpath+"/"+db+","+fullpath+"/"+db+"_1"
    #   shutil.copy2("db.sqlite3",fullpath+"/db.sqlite3") # copy new current
   
   #if type == "initial":
   #    if len(vs)>0 or len(os.listdir(path+"/versions")):
   #        print "folders are not empty, please remove old files berfore initiating"
   #    else:
   #        shutil.copy2("db.sqlite3",fullpath+"/db.sqlite3")
#        shutil.copy2("db.sqlite3",path+"/versions/db.sqlite3")
##            os.symlink(path+"/versions/db.sqlite3",path+"/current/db.sqlite3")

