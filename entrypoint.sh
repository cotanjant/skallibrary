#!/bin/sh
set -e

mkdir -p /app/media

# PostgreSQL hazır olana kadar bekle (Konteyner soğuk başlangıç yarış durumunu önler)
python -c "
import time, os, sys
db_url = os.environ.get('DATABASE_URL', '')
if db_url and db_url.startswith(('postgres://', 'postgresql://')):
    import psycopg
    print('PostgreSQL veritabani baglantisi bekleniyor...')
    for attempt in range(1, 31):
        try:
            with psycopg.connect(db_url, connect_timeout=3):
                print('PostgreSQL baglantisi basarili.')
                break
        except Exception as e:
            if attempt == 30:
                print(f'Hata: 30 saniye icinde veritabanina erisilemedi: {e}', file=sys.stderr)
                sys.exit(1)
            time.sleep(1)
"

python manage.py migrate --noinput
python manage.py purge_graduated_students

exec "$@"
