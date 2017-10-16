#!/usr/bin/env bash

cd .. #change into copf2 setting direction
python manage.py makemigrations  ## should return nothing
python manage.py migrate  ## database created

python extra_files/copf2.py -t "init"