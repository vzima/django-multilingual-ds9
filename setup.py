# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages

# TODO: Update __init__ to enable this version import
#version = __import__('multilingual').__version__
version = '0.3.1'


setup(name='django-multilingual-ds9',
      version=version,
      description='Multilingual extension for Django - Deep Space 9',
      author='Vlastimil Zíma',
      url='http://github.com/vzima/django-multilingual-ds9',
      packages=find_packages(exclude=['tests', 'tests.*']),
      zip_safe=False,
      package_data={'multilingual': ['templates/multilingual/admin/*.html', 'flatpages/templates/flatpages/*.html',
                                     'static/multilingual/css/admin_styles.css'],
                    'multilingual.flatpages': ['templates/flatpages/*.html', ]})
