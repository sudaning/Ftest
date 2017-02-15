#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
from optparse import OptionParser
import os,sys

if __name__ == '__main__':
	
	parser = OptionParser()
	parser.add_option('-i', '--addrs', dest='addrs', default='10.0.33.54:7000,10.0.33.54:7001', help='redis server IP address')
	parser.add_option('-l', '--lib', dest='lib', metavar="lib file directory", default='../lib', help='lib directory [default: %default]')
	(options, args) = parser.parse_args()  

	run_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
	sys.path.append(os.path.join(run_path, options.lib))
	import redisCluterBee
	r = redisCluterBee.redisCluterBee(options.addrs, debug=False)
	try:
		r.get('testing')	
		print("INFO:connect redis success. addrs:%s" % (options.addrs))
		print(0)
	except Exception as err:
		print("ERR: " + str(err))
		print(1)

