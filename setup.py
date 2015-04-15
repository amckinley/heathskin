#!/usr/bin/env python

from distutils.core import setup

setup(name='Heathskin',
      version='1.0',
      description='Heathstone log uploader and processor',
      author='Austin McKinley',
      author_email='bearontheroof@gmail.com',
      packages=['heathskin'],
      scripts=['bin/heathskin-uploader', 'bin/heathskin-frontend', 'bin/heathskin-replayer'],
      url='https://github.com/amckinley/heathskin',
     )
