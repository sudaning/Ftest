#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

#
#
#

from optparse import OptionParser
import os,sys
import threading
import time
import uuid

if __name__ == '__main__':
	
	parser = OptionParser()
	# 用哪个freeswitch发起该呼叫
	parser.add_option('--host', dest='host', help='FreeSWITCH server IP address')
	parser.add_option('--port', dest='port', default=8021, help='FreeSWITCH server event socket port')
	parser.add_option('--password', dest='password', default='ClueCon', help='ESL password')
	parser.add_option('--timeout', dest='timeout', type='int', default=15, help='timeout')

	parser.add_option('-l', '--lib', dest='lib', default='../lib', help='lib directory [default: %default]')

	# 主叫号码
	parser.add_option('--caller_num', dest='caller_num', help='caller number')
	# 被叫号码
	parser.add_option('--callee_num', dest='callee_num', help='callee number')
	# 向哪个服务器发起该呼叫
	parser.add_option('--server_ip', dest='server_ip', help='server IP')
	parser.add_option('--server_port', dest='server_port', help='server IP')

	# answer之后的hangup间隔时间(单位:秒)，-1代表不hangup
	parser.add_option('--hangup_time', dest='hangup_time', type='int', default=-1, help='hangup time')
	# ring之后的cancel间隔时间(单位:秒)，-1代表不cancel
	parser.add_option('--cancel_time', dest='cancel_time', type='int', default=-1, help='cancel time')

	(options, args) = parser.parse_args()  

	run_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
	sys.path.append(os.path.join(run_path, options.lib))
	from neko import ESLEvent

	# 初始化一个发起呼叫的ESL
	Call = ESLEvent(options.host, options.port, options.password)

	call_uuid = None

	# 接收呼叫信息ESL定义
	class CallerEvent(ESLEvent):
		
		def __init__(self, ip, port, password):
			ESLEvent.__init__(self, ip, port, password)
			pass

		def channel_event(self, event):
			event_name = event.getHeader("Event-Name")
			event_sub_name = event.getHeader("Event-Subclass")

			if event_name in ['CHANNEL_CREATE']:
				return self.channel_create(event)
			elif event_name in ['CHANNEL_PROGRESS', 'CHANNEL_PROGRESS_MEDIA']:
				return self.channel_progress(event)
			elif event_name in ['CHANNEL_ANSWER']:
				return self.channel_answer(event)
			elif event_name in ['CHANNEL_HANGUP']:
				return self.channel_hangup(event)

		def channel_create(self, event):
			uuid = event.getHeader("unique-id")
			session_id = event.getHeader("variable_session_id")
			if call_uuid == uuid:
				print("INFO:generated a call %s --> %s" % (event.getHeader("Caller-Caller-ID-Number"), event.getHeader("Caller-Destination-Number")))

		def channel_progress(self, event):
			uuid = event.getHeader("unique-id")
			session_id = event.getHeader("variable_session_id")
			if call_uuid == uuid:
				print("INFO:call ringing")
				if options.cancel_time != -1:
					time.sleep(options.cancel_time)
					# 挂机
					Call.esl().api("uuid_kill", call_uuid)
				
		def channel_answer(self, event):
			uuid = event.getHeader("unique-id")
			session_id = event.getHeader("variable_session_id")
			if call_uuid == uuid:
				print("INFO:call answered")
				if options.hangup_time != -1:
					time.sleep(options.hangup_time)
					# 挂机
					Call.esl().api("uuid_kill", call_uuid)
				

		def channel_hangup(self, event):
			uuid = event.getHeader("unique-id")
			session_id = event.getHeader("variable_session_id")
			if call_uuid == uuid:
				print("INFO:call hangup")
				print(0)
				return "end"

	class callEventThread(threading.Thread):
		def __init__(self):
			threading.Thread.__init__(self)

		def run(self):
			c = CallerEvent(options.host, options.port, options.password)
			c.run(options.timeout)

	# 开启呼叫事件接收线程
	callEvent = callEventThread()
	callEvent.start()
	time.sleep(1)

	# 生成一个UUID给freeswitch，后续用此UUID监控呼叫相关事件。
	call_uuid = str(uuid.uuid4())
	org_argv = "{origination_caller_id_number=%s,origination_uuid=%s}sofia/external/sip:%s@%s:%s &park" \
		% (options.caller_num, call_uuid, options.callee_num, options.server_ip, options.server_port)
	
	# 开始呼叫
	Call.esl().api("originate", org_argv)



		