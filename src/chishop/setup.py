#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

chishop = __import__('chishop', {}, {}, [''])

tests_require = [
    'djangopypi==0.4.4-isotoma9',
    'South==0.7.1',
    'Django==1.3',
    'django-registration',
    'django-haystack',
    'Whoosh==1.8.2',
]

setup(
    name='chishop',
    version="0.1.1-isotoma11",
    description='Simple PyPI server written in Django.',
    author='Ask Solem',
    author_email='askh@opera.com',
    packages=find_packages(),
    include_package_data=True,
    url="http://ask.github.com/chishop",
    zip_safe=False,
    install_requires=[
        'djangopypi==0.4.4-isotoma9',
        'South==0.7.1',
        'Django==1.3',
        'django-registration',
        'django-haystack==1.1.0',
        'Whoosh==1.8.2',
    ],
    dependency_links=[
        'https://bitbucket.org/ubernostrum/django-registration/downloads/django-registration-0.8-alpha-1.tar.gz#egg=django-registration',
        'https://github.com/disqus/djangopypi/tarball/master#egg=djangopypi',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Topic :: System :: Software Distribution",
        "Programming Language :: Python",
    ],
    tests_require=tests_require,
    extras_require={'test': tests_require},
)
