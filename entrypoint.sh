#!/bin/bash

set -e

echo "${0}: running migrations."
python3 manage.py makemigrations
python3 manage.py migrate --noinput

echo "${0}: starting server."
python3 manage.py runserver 0.0.0.0:8080