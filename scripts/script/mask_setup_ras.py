#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
from optparse import OptionParser
import os,sys

if __name__ == '__main__':

	parser = OptionParser()
	parser.add_option('--host', dest='host', help='FreeSWITCH server IP address')
	parser.add_option('--port', dest='port', default='8021', help='FreeSWITCH server event socket port')
	parser.add_option('--password', dest='password', default='ClueCon', help='ESL password')

	parser.add_option('--route_host', dest='route_host', help='bridge call to host ip')
	parser.add_option('--route_port', dest='route_port', help='bridge call to host port')

	parser.add_option('-l', '--lib', dest='lib', metavar="lib file directory", default='../lib', help='lib directory [default: %default]')
	(options, args) = parser.parse_args()  

	run_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
	sys.path.append(os.path.join(run_path, options.lib))

	try:
		import ESL

		esl = ESL.ESLconnection(options.host, options.port, options.password)
		if esl.connected():
			esl.api("global_setvar", "IMSaddr=%s:%s" % (options.route_host, options.route_port))
			print("INFO:set IMSaddr: %s:%s" % (options.route_host, options.route_port))
			print(0)
		else:
			print("ERR :connect freeswitch ESL failed. %s:%s@%s" % (options.host, options.port, options.password))
			print(1)
		esl.disconnect()
	except Exception as err:
		print("ERR: " + str(err))
		print(1)

