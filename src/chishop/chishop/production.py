import os
import chishop
from chishop.conf.default import *

DEBUG = True
TEMPLATE_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE' : 'django.db.backends.sqlite3',
        'NAME' : os.path.join(os.path.abspath(os.path.dirname(chishop.__file__)), 'devdatabase.db'),
        'USER' : '',
        'PASSWORD' : '',
        'HOST' : '',
        'PORT' : '',
    }
}

HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_SITECONF = 'chishop.search_sites'
HAYSTACK_WHOOSH_PATH = os.path.join(os.path.dirname(chishop.__file__), 'haystack')

LOGFILE = '/var/log/chishop/chishop.log'

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'log_file':{
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGFILE,
            'maxBytes': '16777216', # 16megabytes
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
        }
    }
}
