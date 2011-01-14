import sys, os
from setuptools import setup, find_packages

import adhoc

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='adhoc',
      version=adhoc.__version__,
      description='A Command-line XMPP Ad-Hoc Commands Runner',
      long_description=read('README'),
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'License :: OSI Approved :: MIT',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
      keywords='xmpp sleekxmpp ad-hoc adhoc',
      author='Lance Stout',
      author_email='lancestout@gmail.com',
      url='http://github.com/legastero/adhoc',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      scripts=['scripts/adhoc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['sleekxmpp'])
