###################################################################
#  This file serves as a base configuration for testing purposes  #
#  only. It is not intended for production use.                   #
###################################################################

import logging

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'NAME': 'netbox',
        'USER': 'netbox',
        'PASSWORD': 'netbox',
        'HOST': 'localhost',
        'PORT': '',
        'CONN_MAX_AGE': 300,
    }
}

PLUGINS = [
    'netbox.tests.dummy_plugin',
    'netbox.tests.dummy_plugin_b',
]

RQ = {
    'COMMIT_MODE': 'auto',
}

REDIS = {
    'tasks': {
        'HOST': 'localhost',
        'PORT': 6379,
        'USERNAME': '',
        'PASSWORD': '',
        'DATABASE': 0,
        'SSL': False,
    },
    'caching': {
        'HOST': 'localhost',
        'PORT': 6379,
        'USERNAME': '',
        'PASSWORD': '',
        'DATABASE': 1,
        'SSL': False,
    }
}

SECRET_KEY = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

DEFAULT_PERMISSIONS = {}

API_TOKEN_PEPPERS = {
    1: 'TEST-VALUE-DO-NOT-USE-TEST-VALUE-DO-NOT-USE-TEST-VALUE-DO-NOT-USE',
}


class MissingSnapshotHandler(logging.Handler):
    """
    Fail any update saved without calling snapshot() first, which would otherwise fall back to reading the
    pre-change data from the database.
    """
    def emit(self, record):
        if record.funcName == 'snapshot_from_db':
            raise AssertionError(record.getMessage())


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'missing_snapshot': {
            '()': MissingSnapshotHandler,
        },
    },
    'loggers': {
        'netbox.models.features': {
            'handlers': ['missing_snapshot'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
