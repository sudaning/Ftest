#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

from optparse import OptionParser
import os,sys
import datetime

if __name__ == '__main__':
	
	parser = OptionParser()
	parser.add_option('--addrs', dest='addrs')
	parser.add_option('--lib', dest='lib', default='../lib')
	parser.add_option('--sipp_num', dest='sipp_num')
	parser.add_option('--accountid', dest='accountid')
	parser.add_option('--appid', dest='appid')
	parser.add_option('--record', dest='record', type='int')
	parser.add_option('--dis_num', dest='dis_num')
	parser.add_option('--forbidden', dest='forbidden', type='int')
	parser.add_option('--sipp_sipp', dest='sipp_sipp', type='int')
	parser.add_option('--roam', dest='roam', type='int')
	parser.add_option('--home_area', dest='home_area')
	(options, args) = parser.parse_args()  

	run_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
	sys.path.append(os.path.join(run_path, options.lib))

	data = []
	
	try:
		from neko import redisCluterBee
		r = redisCluterBee(options.addrs)

		stamp = ('SIPPHONE:SIP:STAMP:%s' % (options.sipp_num), datetime.datetime.now().strftime("%Y%m%d%H%M%S")) #时间作为时戳
		r.set(*stamp)
		print("INFO:build sipphone number stamp info success. %s --> %s" % stamp)
		data.append(stamp)

		key = options.sipp_num
		function = options.forbidden + (options.sipp_sipp << 1) + (options.roam << 2)
		value = [options.accountid, options.appid, str(options.record), options.dis_num, str(function), options.home_area]
		sipphone = ('SIPPHONE:SIP:%s' % (key), '_'.join(value))
		r.set(*sipphone)
		print("INFO:build sipphone number info success. %s --> %s" % sipphone)
		data.append(sipphone)

		account = ("APP&ACCOUNT_STATUS:%s" % (options.appid), "0")
		r.set(*account)
		data.append(account)
		print("INFO:build sipphone account success. %s --> %s" % account)
		print(0)
	except Exception as err:
		for x in data:
			print("INFO:destroy data. %s" % (x[0]))
			r.delete(x[0])
		print("ERR: " + str(err))
		print(1)
