#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

from optparse import OptionParser
import os,sys

if __name__ == '__main__':
	
	parser = OptionParser()
	parser.add_option('-s', '--host', dest='host', default='10.9.0.42', help='ras ssh server IP address')
	parser.add_option('-p', '--port', dest='port', default='22', help='ras ssh server port')
	parser.add_option('-u', '--user', dest='user', default='root', help='ssh user')
	parser.add_option('-a', '--password', dest='password', default='root', help='ssh password')
	
	parser.add_option('-l', '--lib', dest='lib', metavar="lib file directory", default='../lib', help='lib directory [default: %default]')
	
	(options, args) = parser.parse_args()  

	run_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
	sys.path.append(os.path.join(run_path, options.lib))
	from neko import Ssh
	
	try:
		ssh = Ssh(options.host, options.port, options.user, options.password)
		print(0)
	except Exception as err:
		print(err)
		print(1)
