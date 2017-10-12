import requests
import json
from requests.auth import HTTPBasicAuth


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


def correctforskalle(sample_id,**corrections):
    passw='zBLOf2@7'
    user='Elin.Axelsson'
    s = requests.Session()
    auth = { 'username': user , 'password': passw }
    r = s.post('http://ngs.csf.ac.at/forskalle/api/login', data=auth)
    if (r.status_code != 200):
        raise Exception('Authentication error?')
    r = s.get('http://ngs.csf.ac.at/forskalle/api/samples/'+str(sample_id))
    if (r.status_code != 200):
        raise Exception('get error')
    sample = r.json()
    for kw in corrections:
        if sample[kw] != corrections[kw]:
            print "got: " + sample[kw]
            print "want: " + corrections[kw]
            sample[kw] = corrections[kw]
            print sample[kw]
            res=s.post('http://ngs.csf.ac.at/forskalle/api/samples/'+str(sample_id), json=sample)
            if (res.status_code != 200):
                raise Exception('Post error')
            print res.json()[kw] ###
