#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
from optparse import OptionParser
import os,sys

if __name__ == '__main__':
	
	parser = OptionParser()
	parser.add_option('--host', dest='host')
	parser.add_option('--port', dest='port')
	parser.add_option('--password', dest='password')
	
	parser.add_option('-l', '--lib', dest='lib', default='../lib')
	(options, args) = parser.parse_args()  

	run_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
	sys.path.append(os.path.join(run_path, options.lib))

	try:
		import ESL

		esl = ESL.ESLconnection(options.host, options.port, options.password)
		if esl.connected():
			# IMS地址
			esl.api("reloadxml", "")
			print("INFO:reloadxml")
			
			esl.disconnect()
			print(0)
		else:
			print("ERR :connect freeswitch ESL failed. %s:%s@%s" % (options.host, options.port, options.password))
			print(1)
		
	except Exception as err:
		print("ERR: " + str(err))
		print(1)

