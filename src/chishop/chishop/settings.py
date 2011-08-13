import os
import chishop
from chishop.conf.default import *

DEBUG = True
TEMPLATE_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE' : 'sqlite3',
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
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.abspath(os.path.dirname(chishop.__file__)), 'logs/chishop.log'),
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
