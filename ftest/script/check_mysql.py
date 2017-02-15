#!/usr/bin/env python 
# -*- coding: utf-8 -*-
from optparse import OptionParser 
import os,sys

if __name__ == '__main__':
	
	parser = OptionParser()
	parser.add_option('-s', '--host', dest='host', help='MySQL server IP address')
	parser.add_option('-p', '--port', dest='port', type="int", default=3306, help='MySQL server port')
	parser.add_option('-u', '--user', dest='user', help='MySQL server user')
	parser.add_option('-a', '--password', dest='password', help='MySQL server password')
	parser.add_option('-d', '--dbname', dest='dbname', help='MySQL server dbname')
	parser.add_option('-l', '--lib', dest='lib', metavar="lib file directory", default='../lib', help='lib directory [default: %default]')

	(options, args) = parser.parse_args()  

	run_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
	sys.path.append(os.path.join(run_path, options.lib))

	try:
		from number import MySQL
		
		conn = MySQL(host = options.host,
	        port = options.port,
	        user = options.user,
	        password = options.password,
	        dbname = options.dbname)
		if conn:
			print("INFO:connect mysql success. %s:%d@%s:%s->%s" % 
				(options.host, options.port, options.user, options.password, options.dbname))
			print(0)

	except Exception as err:
		print("ERR :connect mysql failed. %s:%d@%s:%s->%s" % 
			(options.host, options.port, options.user, options.password, options.dbname))
		print(1)
	
