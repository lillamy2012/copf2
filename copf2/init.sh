#!/usr/bin/env bash

python manage.py makemigrations  ## should return nothing
python manage.py migrate  ## database created
python copf2.py -t "initial"