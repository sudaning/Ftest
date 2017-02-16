#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

from optparse import OptionParser
import os,sys

if __name__ == '__main__':
	
	parser = OptionParser()
	parser.add_option('-i', '--addrs', dest='addrs', help='redis server IP address')
	parser.add_option('-l', '--lib', dest='lib', metavar="lib file directory", default='../lib', help='lib directory [default: %default]')
	parser.add_option('-a', '--anum', dest='anum', metavar="a number", help='A number')
	parser.add_option('-m', '--hiddennum', dest='hnum', metavar="hidden number", help='hidden number')
	parser.add_option('-b', '--bnum', dest='bnum', metavar="b number", help='B number')
	parser.add_option('-r', '--record', dest='record', metavar="record or not", type='int', help='record or not')
	parser.add_option('-p', '--appid', dest='appid', metavar="appid", help='appid')
	parser.add_option('-t', '--accountid', dest='accountid', metavar="accountid", help='accountid')
	parser.add_option('-s', '--appid_status', dest='appid_status', metavar="appid_status", help='appid status')
	(options, args) = parser.parse_args()  

	run_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
	sys.path.append(os.path.join(run_path, options.lib))
	from neko import redisCluterBee
	r = redisCluterBee(options.addrs)
	try:
		key = [options.anum, options.hnum]
		value = [options.bnum, str(options.record), options.appid, options.accountid]
		mask_data = ('mask:' + '_'.join(key), '_'.join(value))
		r.set(*mask_data)
		print("INFO: build mask number info success. %s --> %s" % mask_data)

		mask_account = ("APP&ACCOUNT_STATUS:" + options.appid, options.appid_status)
		r.set(*mask_account)
		print("INFO: build mask account success. %s --> %s" % mask_account)

		print(0)
	except Exception as err:
		print("ERR: " + str(err))
		print(1)
