#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

from optparse import OptionParser
import os,sys

if __name__ == '__main__':
	
	parser = OptionParser()
	parser.add_option('--addrs', dest='addrs')
	parser.add_option('--lib', dest='lib', default='../lib')
	parser.add_option('--sipp_num', dest='sipp_num')
	parser.add_option('--appid', dest='appid', default='')
	(options, args) = parser.parse_args()  

	run_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
	sys.path.append(os.path.join(run_path, options.lib))
	
	try:
		from neko import redisCluterBee
		r = redisCluterBee(options.addrs)

		stamp = 'SIPPHONE:SIP:STAMP:%s' % (options.sipp_num)
		r.delete(stamp)
		print("INFO:destroy sipphone number stamp info success. %s" % (stamp))

		sipphone = 'SIPPHONE:SIP:%s' % (options.sipp_num)
		r.delete(sipphone)
		print("INFO:destroy sipphone number info success. %s" % (sipphone))

		if options.appid:
			account = "APP&ACCOUNT_STATUS:%s" % (options.appid)
			r.delete(account)
			print("INFO:destroy sipphone account success. %s" % (account))
		
		print(0)
	except Exception as err:
		print("ERR: " + str(err))
		print(1)
