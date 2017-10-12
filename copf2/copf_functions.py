import requests
import json
from requests.auth import HTTPBasicAuth
import pandas as pd
import numpy as np



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

