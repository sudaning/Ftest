from setuptools import find_packages, setup
from ftest import __version__ as version

author = 'Daning Su'
author_email = 'sudaning@sina.com'
description = "A pure Python library designed to auto-test for FREESWITCH easy "

with open('README.rst') as f:
    long_description = f.read()

with open('./requirements.txt', 'r') as f:
	 requirements = f.readlines()
	 install_requires = [x for x in requirements if (x and x[0] != '#')]

license = 'LICENSE'

name = 'pyFtest'
packages = [
	'ftest',
]
platforms = ['linux']
url = 'https://github.com/sudaning/Ftest'
download_url = ''
classifiers = [
	'Development Status :: 5 - Production/Stable',
	'Intended Audience :: Science/Research',
	'Natural Language :: Chinese (Simplified)',
	'Topic :: Text Processing',
	'Operating System :: POSIX :: Linux',
	'License :: OSI Approved :: MIT License',
	'Programming Language :: Python :: 2',
	'Programming Language :: Python :: 2.7',
]

setup(author=author,
	author_email=author_email,
	description=description,
	license=license,
	long_description=long_description,
	install_requires=install_requires,
	maintainer=author,
	name=name,
	packages=find_packages(),
	platforms=platforms,
	url=url,
	download_url=download_url,
	version=version,
	classifiers=classifiers,
)

