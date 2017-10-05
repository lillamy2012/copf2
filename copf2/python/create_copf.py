#!/usr/bin/env bash

backuppath="/Users/elin.axelsson/berger_group/user/elin.axelsson/copf2_backups" ## group folder (is backuped)
cd .. #change into copf2 setting direction
python manage.py makemigrations  ## should return nothing
python manage.py migrate  ## database created
python copf2_pop.py -d "99+years" ## setup all files from group
mkdir -p $backuppath/initial
mv group_99_years.json $backuppath/initial/group_99_years.json ## no changes done to forskalle
cp db.sqlite3 $backuppath/initial/db.sqlite3 # as forskalle
python copf2_pop.py -t ## clean up tissue_type
mkdir -p $backuppath/current
mkdir -p $backuppath/versions
cp db.sqlite3 $backuppath/versions/db.sqlite3 # now tissue cleaned, in future rename and link newest
ln -s $backuppath/versions/db.sqlite3 $backuppath/current/db.sqlite3

