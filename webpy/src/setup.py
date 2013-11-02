#!/usr/bin/env python

# ...

# here is an article about setup.py file
# url: http://minixalpha.github.io/StrayBirds/%E6%8A%80%E6%9C%AF/2013/11/01/pypkg.html

from distutils.core import setup
from web import __version__

setup(name='web.py',
      version=__version__,
      description='web.py: makes web apps',
      author='Aaron Swartz',
      author_email='me@aaronsw.com',
      maintainer='Anand Chitipothu',
      maintainer_email='anandology@gmail.com',
      url=' http://webpy.org/',
      packages=['web', 'web.wsgiserver', 'web.contrib'],
      long_description="Think about the ideal way to write a web app. Write the code to make it happen.",
      license="Public domain",
      platforms=["any"],
     )
