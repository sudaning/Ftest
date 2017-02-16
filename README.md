#Welcome to Ftest
![](https://travis-ci.org/sudaning/Ftest.svg?branch=master)
![](https://img.shields.io/pypi/v/pyFtest.svg)
![](https://img.shields.io/badge/python-3.5-green.svg)
![](https://img.shields.io/badge/python-2.7-green.svg)
![](https://img.shields.io/badge/docs-stable-brightgreen.svg?style=flat)
![](https://img.shields.io/github/stars/sudaning/Ftest.svg)
![](https://img.shields.io/github/forks/sudaning/Ftest.svg)

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
import os
from neko import caseMgr

run_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
config_file_path = os.path.join(run_path, 'packet/demo_config.yaml')
packet_file_path = os.path.join(run_path, 'packet/demo_packet.yaml')
script_dir_path = os.path.join(run_path, 'script')
report_dir_path = os.path.join(run_path, 'report')

c = caseMgr(config_file_path, packet_file_path, script_dir_path)
c.load() and c.run('xls', report_dir_path, True, False)
```

##From the author
**Welcome to use pyFtest (●'◡'●)ﾉ♥**  
If you find any bug, please report it to me by opening a issue.
pyNeko needs to be improved, your contribution will be welcomed.
