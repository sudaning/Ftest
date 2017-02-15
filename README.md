#Welcome to Neko
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
import time  
from neko import ProcBar, color_str  
p = ProcBar(mod='details')  
total = 56  
p.set_details(total, widget_type="percent").start("Dance up...")  
for i in range(0, total + 1):  
    if p.move():  
    time.sleep(0.1)  
p.stop(color_str("ending", "sky_blue"))
```

##From the author
**Welcome to use pyFtest (●'◡'●)ﾉ♥**  
If you find any bug, please report it to me by opening a issue.
pyNeko needs to be improved, your contribution will be welcomed.
