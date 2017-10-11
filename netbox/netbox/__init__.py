from distutils.version import StrictVersion

from django.db import connection


# NetBox v2.2 and later requires PostgreSQL 9.4 or higher
with connection.cursor() as cursor:
    cursor.execute("SELECT VERSION()")
    row = cursor.fetchone()
    pg_version = row[0].split()[1]
    if StrictVersion(pg_version) < StrictVersion('9.4.0'):
        raise Exception("PostgreSQL 9.4.0 or higher is required. ({} found)".format(pg_version))
