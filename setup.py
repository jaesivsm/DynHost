#!/usr/bin/env python3
from setuptools import setup


with open('README.md') as fd:
    readme = fd.read()

setup(name='DynHost',
      version='1.0.5',
      description='Multiple DynDNS updating script',
      long_description=readme,
      keywords='dynhost dyndhs ovh',
      classifiers=[
          "Intended Audience :: System Administrators",
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Topic :: Internet :: Name Service (DNS)",
          "Topic :: System :: Networking"],
      license="GPLv3",
      author="François Schmidts",
      author_email="francois@schmidts.fr",
      maintainer="François Schmidts",
      maintainer_email="francois@schmidts.fr",
      scripts=['dynhost'],
      packages=['dynhost_lib'],
      url='https://github.com/jaesivsm/DynHost',
      install_requires=['requests>=2.10.0'],
      data_files=[('', ['dynhost.service', 'README.md'])],
      )
