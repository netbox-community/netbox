"""Minimal NetBox configuration used by the wheel-install smoke test."""

import os
from pathlib import Path

BASE_DIR = Path(os.getenv('NETBOX_SMOKETEST_BASE', '/tmp/netbox-smoketest'))
BASE_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_HOSTS = ['*']
API_TOKEN_PEPPERS = {
    1: os.getenv('NETBOX_SMOKETEST_API_TOKEN_PEPPER', 'a' * 50),
}
SECRET_KEY = os.getenv('NETBOX_SMOKETEST_SECRET_KEY', 'b' * 50)

DATABASES = {
    'default': {
        'NAME': os.getenv('POSTGRES_DB', 'netbox'),
        'USER': os.getenv('POSTGRES_USER', 'netbox'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'netbox'),
        'HOST': os.getenv('POSTGRES_HOST', '127.0.0.1'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
        'CONN_MAX_AGE': 0,
    }
}

REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS = {
    'tasks': {
        'HOST': REDIS_HOST,
        'PORT': REDIS_PORT,
        'PASSWORD': os.getenv('REDIS_PASSWORD', ''),
        'DATABASE': int(os.getenv('REDIS_TASKS_DATABASE', '0')),
        'SSL': False,
    },
    'caching': {
        'HOST': REDIS_HOST,
        'PORT': REDIS_PORT,
        'PASSWORD': os.getenv('REDIS_PASSWORD', ''),
        'DATABASE': int(os.getenv('REDIS_CACHING_DATABASE', '1')),
        'SSL': False,
    },
}

# STATIC_ROOT is fixed to <NETBOX_ROOT>/static; the workflow sets NETBOX_ROOT to the scratch base.
MEDIA_ROOT = str(BASE_DIR / 'media')
REPORTS_ROOT = str(BASE_DIR / 'reports')
SCRIPTS_ROOT = str(BASE_DIR / 'scripts')

for path in (MEDIA_ROOT, REPORTS_ROOT, SCRIPTS_ROOT):
    Path(path).mkdir(parents=True, exist_ok=True)
