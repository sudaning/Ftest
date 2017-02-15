#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
from optparse import OptionParser
import os,sys

if __name__ == '__main__':
	
	parser = OptionParser()
	parser.add_option('-s', '--host', dest='host', help='FreeSWITCH server IP address')
	parser.add_option('-p', '--port', dest='port', default='8021', help='FreeSWITCH server event socket port')
	parser.add_option('-a', '--password', dest='password', default='ClueCon', help='ESL password')
	parser.add_option('-l', '--lib', dest='lib', metavar="lib file directory", default='../lib', help='lib directory [default: %default]')
	(options, args) = parser.parse_args()  

	run_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
	sys.path.append(os.path.join(run_path, options.lib))

	try:
		from pyesl import ESLEvent
		esl = ESLEvent(options.host, options.port, options.password)
		if esl and esl.connected():
			print("INFO:connect freeswitch ESL success. %s:%s@%s" % (options.host, options.port, options.password))
			print(0)
		else:
			print("ERR :connect freeswitch ESL failed. %s:%s@%s" % (options.host, options.port, options.password))
			print(1)
	except Exception as err:
		print("ERR: " + str(err))
		print(1)

