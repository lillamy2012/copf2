import requests
import json
import os
import pandas as pd
import numpy as np
import shutil
import sys, getopt

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


def read_json(jsonf):
    with open(jsonf, 'r') as json_file:
        data = json.load(json_file)
    return data

def readin_csv(csv):
    df = pd.read_csv(csv,sep=";") #,dtype={'Sample Id': np.int64})
    df.dropna(how="all", inplace=True)
    df[['Sample Id']]= df[['Sample Id']].apply(pd.to_numeric,downcast='integer')
    return(df)

def updateSheet(sheet):
    data = readin_csv(sheet)
    if not {'Antibody', 'Celltype', 'Comments', 'Descr','Organism','Tissue Type','Treatment','Library prep','Sample Id'}.issubset(data.columns):
        print 'file is missing column'
        sys.exit(2)
    
    columnsToUse=['Antibody', 'Celltype', 'Comments', 'Descr','Organism','Tissue Type','Treatment','Library prep','Sample Id']
    data = data[columnsToUse]
    data.columns = ['antibody', 'celltype', 'comments', 'descr','organism','tissue_type','treatment','preparation_kit','sample id']
    dd = data.to_dict(orient='records')
    return(dd)

def backupDB(type,db="db.sqlite3",path="/Users/elin.axelsson/berger_group/user/elin.axelsson/copf2_backups"):
    if type not in [ "versions","initial"]:
        print "wrong type"
        sys.exit(2)
    fullpath = path+"/"+type
    vs=os.listdir(fullpath)
    if type == "versions":
        name=db+"_"
        fname = [s for s in vs if name in s] #
        num = [ int(s.split('_')[1]) for s in fname ]
        Z = [ x for _,x in sorted(zip(num,fname))]
        Y = sorted(num)
        for i in range(len(Y)-1,-1,-1): # rename all existing except current
            shutil.copy2(fullpath+"/"+Z[i],fullpath+"/"+name+str(Y[i]+1))
            print fullpath+"/"+Z[i]+","+fullpath+"/"+name+str(Y[i]+1)

        shutil.copy2(fullpath+"/"+db,fullpath+"/"+db+"_1") # rename current
        print fullpath+"/"+db+","+fullpath+"/"+db+"_1"
        shutil.copy2("db.sqlite3",fullpath+"/db.sqlite3") # copy new current
   
    if type == "initial":
        if len(vs)>0 or len(os.listdir(path+"/versions")):
            print "folders are not empty, please remove old files berfore initiating"
        else:
            shutil.copy2("db.sqlite3",fullpath+"/db.sqlite3")
            shutil.copy2("db.sqlite3",path+"/versions/db.sqlite3")
            os.symlink(path+"/versions/db.sqlite3",path+"/current/db.sqlite3")

