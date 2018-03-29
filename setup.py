"""A setuptools based setup module for Zippy-Ip-Scanner"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from codecs import open
from os import path
from setuptools import setup, find_packages

from zippyipscanner.version import __version__

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open(path.join(here, 'HISTORY.rst'), encoding='utf-8') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
    'wxPython',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='Zippy-Ip-Scanner',
    version=__version__,
    description="IP Scanner",
    long_description=readme + '\n\n' + history,
    author="Simon Wu",
    author_email='swprojects@runbox.com',
    url='https://github.com/swprojects/zippy-ip-scanner',
    include_package_data=True,
    install_requires=requirements,
    license="GPLv2",
    classifiers=[
        # 'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
)
