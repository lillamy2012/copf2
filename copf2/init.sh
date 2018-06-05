#!/usr/bin/env bash

echo "makemigrations"
python manage.py makemigrations  ## should return nothing
echo "migrate"
python manage.py migrate  ## database created
echo "initial"
python copf2.py -t "initial"


#$ python manage.py migrate --run-syncdb
