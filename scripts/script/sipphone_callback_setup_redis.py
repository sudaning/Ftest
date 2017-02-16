#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

from optparse import OptionParser
import os,sys
import datetime

max_sipp_num = 10

if __name__ == '__main__':
	
	parser = OptionParser()
	parser.add_option('--addrs', dest='addrs')
	parser.add_option('--lib', dest='lib', default='../lib')
	parser.add_option('--dis_num', dest='dis_num')
	parser.add_option('--accountid', dest='accountid')
	parser.add_option('--appid', dest='appid')
	parser.add_option('--record', dest='record', type='int')
	parser.add_option('--mode', dest='mode') #first_ring sync_ring order_ring
	for i in range(1, max_sipp_num + 1):
		parser.add_option('--sipp_num%d' % i, dest='sipp_num%d' % i, default='')
	(options, args) = parser.parse_args()

	run_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
	sys.path.append(os.path.join(run_path, options.lib))
	
	data = []
	
	try:
		from neko import redisCluterBee
		r = redisCluterBee(options.addrs)

		stamp = ('SIPPHONE:TEL:STAMP:%s' % (options.dis_num), datetime.datetime.now().strftime("%Y%m%d%H%M%S")) #时间作为时戳
		r.set(*stamp)
		data.append(stamp)
		print("INFO:build sipphone number stamp info success. %s --> %s" % stamp)

		key = options.dis_num
		mode = options.mode in ['first_ring'] and "0" or \
			options.mode in ['sync_ring'] and "1" or \
			options.mode in ['order_ring'] and "2" or "-1"
		if mode == "-1":
			raise Exception("unsupported mode:%s" % (options.mode))

		value1 = [options.accountid, options.appid, str(options.record), mode]
		value2 = filter(lambda x: x != '', [eval('options.sipp_num%d' % x) for x in range(1, max_sipp_num + 1)])
		
		number = ('SIPPHONE:TEL:%s' % (key), '_'.join(value1 + value2))
		r.set(*number)
		data.append(number)
		print("INFO:build sipphone number info success. %s --> %s" % number)

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
