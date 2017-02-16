#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

from optparse import OptionParser
import os,sys

if __name__ == '__main__':
	
	parser = OptionParser()
	parser.add_option('--addrs', dest='addrs', default='10.0.33.54:7000', help='redis server IP address')
	parser.add_option('--lib', dest='lib', metavar="lib file directory", default='../lib', help='lib directory [default: %default]')
	parser.add_option('--anum', dest='anum', metavar="a number", help='A number')
	parser.add_option('--hiddennum', dest='hnum', metavar="hidden number", help='hidden number')
	parser.add_option('--appid', dest='appid', metavar="appid", help='A appid')
	(options, args) = parser.parse_args()  

	run_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
	sys.path.append(os.path.join(run_path, options.lib))
	from neko import redisCluterBee
	r = redisCluterBee(options.addrs)
	try:
		key = [options.anum, options.hnum]
		mask_data = 'mask:' + '_'.join(key)
		r.delete(mask_data)
		print("INFO:destroy mask number info success. " + mask_data)

		mask_account = "APP&ACCOUNT_STATUS:" + options.appid
		r.delete(mask_account)
		print("INFO:destroy mask account success. " + mask_account)
		
		print(0)
	except Exception as err:
		print("ERR: " + str(err))
		print(1)
