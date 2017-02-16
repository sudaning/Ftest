#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
from optparse import OptionParser
import os,sys

if __name__ == '__main__':
	
	parser = OptionParser()
	parser.add_option('-i', '--addrs', dest='addrs', default='10.0.33.54:7000,10.0.33.54:7001', help='redis server IP address')
	(options, args) = parser.parse_args()  

	from neko import redisCluterBee
	r = redisCluterBee(options.addrs, debug=False)
	try:
		r.get('testing')	
		print("INFO:connect redis success. addrs:%s" % (options.addrs))
		print(0)
	except Exception as err:
		print("ERR: " + str(err))
		print(1)

