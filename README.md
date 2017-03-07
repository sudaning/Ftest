#Welcome to Ftest
[![Version][version-badge]][version-link] ![Supported-python-version][python27-badge] [![Build Status][travis-badge]][travis-link]  [![Coverage][coverage-badge]][coverage-link] ![Star][stars] ![Fork][forks] [![MIT License][license-badge]](LICENSE.md)

##Introduction
Ftest is a pure Python library designed to auto-test for secondary development base on FREESWITCH.
You can use Ftest to auto-test FREESWITCH functions easy.
In [/scripts](https://github.com/sudaning/Ftest/tree/master/scripts) , there are some scripts written by me for daily use.

##Installation
1. Via **pip**  
```pip install pyFtest```  
2. Via **easy_install**  
```easy_install pyFtest```
3. From **source**  
```python setup.py install```

##upgrading
1. Via **pip**  
```pip install --upgrade pyFtest```

##Examples

```python
#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

from optparse import OptionParser
import os, sys
from ftest import caseMgr

if __name__ == '__main__':
	
	parser = OptionParser(usage="%prog [--packet] [--config] [--script] [--report] [--rep_mod] [-s] [-r] [--version]", version="%prog 1.1")
	parser.add_option('--packet', dest='packet', default='packet/demo_packet.yaml', help='test pakcet yaml file [default: %default]')
	parser.add_option('--config', dest='config', default='packet/demo_config.yaml', help='config yaml file [default: %default]')
	parser.add_option('--script', dest='script', default='script', help='script directory [default: %default]')
	parser.add_option('--report', dest='report', default='report', help='report directory [default: %default]')
	parser.add_option('--rep_mod', dest='rep_mod', default='xls', help='report mod [default: %default]')
	parser.add_option("-s", action="store_true", dest="silence", help='no any information to show on foreground')  
	parser.add_option("-r", action="store_true", dest="rep_success", help='report successful cases, successful case details to report')
	(options, args) = parser.parse_args()

	run_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
	config_file_path = os.path.join(run_path, options.config)
	packet_file_path = os.path.join(run_path, options.packet)
	script_dir_path = os.path.join(run_path, options.script)
	report_dir_path = os.path.join(run_path, options.report)

	c = caseMgr(config_file_path, packet_file_path, script_dir_path)
	c.load() and c.run(options.rep_mod, report_dir_path, options.rep_success, options.silence)
```

##From the author
**Welcome to use pyFtest (●'◡'●)ﾉ♥**  
If you find any bug, please report it to me by opening a issue.
pyNeko needs to be improved, your contribution will be welcomed.

[version-badge]:   https://img.shields.io/pypi/v/pyFtest.svg?label=pypi
[version-link]:    https://pypi.python.org/pypi/pyFtest/
[python27-badge]:  https://img.shields.io/badge/python-2.7-green.svg
[stars]:           https://img.shields.io/github/stars/sudaning/Ftest.svg
[forks]:           https://img.shields.io/github/forks/sudaning/Ftest.svg
[travis-badge]:    https://img.shields.io/travis/sudaning/Ftest.svg
[travis-link]:     https://travis-ci.org/sudaning/Ftest
[coverage-badge]:  https://img.shields.io/coveralls/sudaning/Ftest.svg
[coverage-link]:   https://coveralls.io/github/sudaning/Ftest
[license-badge]:   https://img.shields.io/badge/license-MIT-007EC7.svg
