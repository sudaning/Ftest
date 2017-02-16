#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
from optparse import OptionParser
import os,sys

if __name__ == '__main__':
	
	parser = OptionParser()
	parser.add_option('-s', '--host', dest='host', help='FreeSWITCH server IP address')
	parser.add_option('-p', '--port', dest='port', default='8021', help='FreeSWITCH server event socket port')
	parser.add_option('-a', '--password', dest='password', default='ClueCon', help='ESL password')
	(options, args) = parser.parse_args()  

	try:
		import neko
		from neko import ESLEvent
		event = ESLEvent(options.host, options.port, options.password)
		print(neko.__file__)
		if event and event.is_connected():
			print("INFO:connect freeswitch ESL success. %s:%s@%s" % (options.host, options.port, options.password))
			print(0)
		else:
			print("ERR :connect freeswitch ESL failed. %s:%s@%s" % (options.host, options.port, options.password))
			print(1)
	except Exception as err:
		print("ERR: " + str(err))
		print(1)

