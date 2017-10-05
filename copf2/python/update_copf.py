#!/usr/bin/env bash

backuppath="/Users/elin.axelsson/berger_group/user/elin.axelsson/copf2_backups" ## group folder (is backuped)
cd .. #change into copf2 setting direction
python copf2_pop.py -d "1+month" ## setup all files from group
python copf2_pop.py -t ## clean up tissue_type - only new samples... no becasue tisssue types can change


for file in $(find output -type f -maxdepth 1)
do
    echo $file
    python copf2_pop.py -r $file
done
#for file in input
#do
#    python copf2_pop.py -c $file
#done


#name=$backuppath/versions/db.sqlite3
#if [[ -e $name ]] ; then ## should always be yes
#    i=0
#    while [[ -e $name-$i ]] ; do
#        let i++
#    done
#    name=$name-$i
#fi
#mv $backuppath/versions/db.sqlite3 $name
#cp db.sqlite3 $backuppath/versions/db.sqlite3


## rename db.sqlite, cp new, link
### to be run 10 and 22 everyday
### update from forskalle
### clean
### review from output
### create from input
### clean
### save db