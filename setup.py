#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import io
import os
import sys
from shutil import rmtree
from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'pdfcli'
DESCRIPTION = 'Simplify manipulating PDFs'
URL = 'https://github.com/oliviersm199/pdfcli'
EMAIL = 'olivier.morissette@gmail.com'
AUTHOR = 'Olivier Simard-Morissette'
REQUIRES_PYTHON = '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*'
VERSION = '0.0.1'
LICENSE = 'MIT'

# What packages are required for this module to be executed?
REQUIRED = ['Click>=7.0, <8.0',
            'PyPDF2>=1.26.0,<2.0']


here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in file!
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

# Load the package's __version__.py module as a dictionary.
about = {}
about['__version__'] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

        sys.exit()


setup(
    name=NAME,
    version=VERSION,
    py_modules=['pdfcli'],
    install_requires=REQUIRED,
    license=LICENSE,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
	description=DESCRIPTION,
    long_description=long_description,
    python_requires=REQUIRES_PYTHON,
    entry_points='''
        [console_scripts]
        pdfcli=pdfcli:cli
    ''',
    cmdclass={
        'upload': UploadCommand,
    }
)
