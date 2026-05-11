#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input

python <<'PY'
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'locoro_app.settings')

import django
django.setup()

from django.core.management import call_command
from django.db import connection


def table_exists(table_name):
    existing_tables = connection.introspection.table_names()
    return table_name in existing_tables


def migration_is_applied(app_label, migration_name):
    if not table_exists('django_migrations'):
        return False

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM django_migrations
            WHERE app = %s AND name = %s
            LIMIT 1
            """,
            [app_label, migration_name],
        )
        return cursor.fetchone() is not None


if table_exists('core_roomimage') and not migration_is_applied('core', '0004_add_roomimage_model'):
    print('core_roomimage already exists. Marking core.0004_add_roomimage_model as applied.')
    call_command('migrate', 'core', '0004_add_roomimage_model', fake=True)

call_command('migrate')
PY
