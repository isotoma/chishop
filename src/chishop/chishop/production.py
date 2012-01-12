
import os
import chishop
from chishop.conf.default import *

DEBUG = False
TEMPLATE_DEBUG = False

DATABASES = {
    'default': {
        'ENGINE' : 'django.db.backends.postgresql_psycopg2',
        'NAME' : 'SET IN BUILDOUT',
        'USER' : 'SET IN BUILDOUT',
        'PASSWORD' : 'SET IN BUILDOUT',
        'HOST' : '',
        'PORT' : '',
    }
}

HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_SITECONF = 'chishop.search_sites'
HAYSTACK_WHOOSH_PATH = os.path.join(os.path.dirname(chishop.__file__), 'haystack')

DJANGOPYPI_RELEASE_UPLOAD_TO = 'SET IN BUILDOUT'
DJANGOPYPI_RELEASE_URL = '/packages/'

LOGFILE = '/var/log/chishop/chishop.log'

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s %(process)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'log_file':{
            'level': 'INFO',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': LOGFILE,
            'formatter': 'verbose',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'djangopypi.views.distutils': {
            'handlers': ['log_file'],
            'level': 'INFO'
        },
        'djangopypi.views.releases': {
            'handlers': ['log_file'],
            'level': 'INFO'
        },
        'djangopypi.auth_logger': {
            'handlers': ['log_file'],
            'level': 'INFO'
        },
    }
}

try:
    from private_settings import *
except ImportError:
    pass
