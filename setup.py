#!/usr/bin/env python3
from setuptools import setup

setup(name='stag',
      version='0.0.1',
      description='cli utility to fill attendance sheet',
      author='Kirill Goldshtein',
      author_email='goldshtein.kirill@gmail.com',
      packages=['stag'],
      install_requires=['google-api-python-client'],
      license='MIT',
      url='https://github.com/go1dshtein/stag',
      classifiers=['Intended Audience :: Developers',
                   'Environment :: Console',
                   'Programming Language :: Python :: 3.3',
                   'Natural Language :: English',
                   'Development Status :: 1 - Planning',
                   'Operating System :: Unix',
                   'Topic :: Utilities'])
