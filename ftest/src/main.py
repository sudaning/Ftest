#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

if __name__ == '__main__':
	from optparse import OptionParser
	parser = OptionParser(usage="%prog [--packet] [--config] [--script] [--report] [--rep_mod] [-l] [-s] [-r] [--version]", version="%prog 1.0")
	parser.add_option('--packet', dest='packet', default='../packet/packet.yaml', help='test pakcet yaml file [default: %default]')
	parser.add_option('--config', dest='config', default='../packet/config.yaml', help='config yaml file [default: %default]')
	parser.add_option('--script', dest='script', default='../script', help='script directory [default: %default]')
	parser.add_option('--report', dest='report', default='../report', help='report directory [default: %default]')
	parser.add_option('-l', '--lib', dest='lib', default='../lib', help='lib directory [default: %default]')
	parser.add_option('--rep_mod', dest='rep_mod', default='xls', help='report mod [default: %default]')
	parser.add_option("-s", action="store_true", dest="silence", help='no any information to show on foreground')  
	parser.add_option("-r", action="store_true", dest="rep_success", help='report successful cases, successful case details to report')
	(options, args) = parser.parse_args()

	import os, sys
	run_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
	sys.path.append(os.path.join(run_path, options.lib))
	from tcase import caseMgr

	config_path = os.path.join(run_path, options.config)
	packet_path = os.path.join(run_path, options.packet)
	script_path = os.path.join(run_path, options.script)
	report_path = os.path.join(run_path, options.report)

	c = caseMgr(config_path, packet_path, script_path)
	c.load() and c.run(options.rep_mod, report_path, options.rep_success, options.silence)


	