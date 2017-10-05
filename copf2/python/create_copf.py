#!/usr/bin/env bash

cd .. #change into copf2 setting direction
python manage.py makemigrations  ## should return nothing
python manage.py migrate  ## database created
python copf2_pop.py -d "99+years" ## setup all files from group
### save db to backup
python copf2_pop.py -t ## clean up tissue_type

