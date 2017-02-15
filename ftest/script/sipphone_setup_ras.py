#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
from optparse import OptionParser
import os,sys

if __name__ == '__main__':
	
	parser = OptionParser()
	parser.add_option('--host', dest='host')
	parser.add_option('--port', dest='port')
	parser.add_option('--password', dest='password')

	parser.add_option('--route_host', dest='route_host')
	parser.add_option('--route_port', dest='route_port')
	parser.add_option('--forbidden_400_95', dest='forbidden_400_95', default='')
	
	parser.add_option('-l', '--lib', dest='lib', default='../lib')
	(options, args) = parser.parse_args()  

	run_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
	sys.path.append(os.path.join(run_path, options.lib))

	try:
		import ESL

		esl = ESL.ESLconnection(options.host, options.port, options.password)
		if esl.connected():
			# IMS地址
			esl.api("global_setvar", "IMSaddr=%s:%s" % (options.route_host, options.route_port))
			print("INFO:set IMSaddr: %s:%s" % (options.route_host, options.route_port))

			# 禁用400、95的呼叫
			if options.forbidden_400_95:
				esl.api("global_setvar", "sipphone_forbidden_call_400_95=%s" % (options.forbidden_400_95))
				print("INFO:set sipphone_forbidden_call_400_95: %s" % (options.forbidden_400_95))
			
			# 数据更新间隔设为1秒
			esl.api("global_setvar", "sipphone_update_period=1")
			print("INFO:set sipphone_update_period: 1")
			
			esl.disconnect()
			print(0)
		else:
			print("ERR :connect freeswitch ESL failed. %s:%s@%s" % (options.host, options.port, options.password))
			print(1)
		
	except Exception as err:
		print("ERR: " + str(err))
		print(1)

