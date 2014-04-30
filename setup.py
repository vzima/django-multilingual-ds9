# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages

VERSION = '0.4.0'


setup(name='django-multilingual-ds9',
      version=VERSION,
      description='Multilingual extension for Django - Deep Space 9',
      author='Vlastimil Zíma',
      url='http://github.com/vzima/django-multilingual-ds9',
      packages=find_packages(),
      package_data={'multilingual': ['templates/multilingual/admin/*.html', 'static/multilingual/css/admin_styles.css'],
                    'multilingual.tests.ml_test_app': ['fixtures/*'],
                    'multilingual.mlflatpages': ['fixtures/*.json'],
                    'multilingual.mlflatpages.tests': ['templates/*.html', 'templates/*/*.html']})
