#!/bin/sh
set -e

mkdir -p /app/media
python manage.py migrate --noinput
python manage.py purge_graduated_students

exec "$@"
