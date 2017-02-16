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
	# 在哪个freeswitch接收呼叫
	parser.add_option('--host', dest='host')
	parser.add_option('--port', dest='port')
	parser.add_option('--password', dest='password')
	parser.add_option('--timeout', dest='timeout', type='int', default=15)

	parser.add_option('-l', '--lib', dest='lib', default='../lib')

	# 主叫号码
	parser.add_option('--caller_num', dest='caller_num', help='caller number')
	# 被叫号码
	parser.add_option('--callee_num', dest='callee_num', help='callee number')

	# 是否有呼叫到来
	parser.add_option('--is_call', dest='is_call', default='yes', help='call or not')

	# 收到invite之后发送ring间隔时间(单位:秒)，-1代表不ring, 0代表立即ring
	parser.add_option('--ring_time', dest='ring_time', type='int', default=-1, help='ring time')

	# 收到invite之后发送answer间隔时间(单位:秒)，-1代表不answer, 0代表立即answer
	parser.add_option('--answer_time', dest='answer_time', type='int', default=-1, help='answer time')

	# 发送hangup间隔时间(单位:秒)，-1代表不hangup
	parser.add_option('--hangup_time', dest='hangup_time', type='int', default=-1, help='hangup time')
	
	(options, args) = parser.parse_args()  

	run_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
	sys.path.append(os.path.join(run_path, options.lib))
	from neko import ESLEvent

	# 接收呼叫信息ESL定义
	class CalleeEvent(ESLEvent):
		
		__call = {}
		__message_flow = {\
			"recv call": {"sequence": 10, "result": False, "describe": "recv calling"},
			"ring": {"sequence": 100, "result": False, "describe": "ring"},
			"answer": {"sequence": 200, "result": False, "describe": "answer"},
			"hangup": {"sequence": 300, "result": False, "describe": "hangup"},
		}

		def __init__(self, ip, port, password):
			ESLEvent.__init__(self, ip, port, password)
			if options.is_call.lower() not in ['yes']:
				self.__message_flow["recv call"]["result"] = True
			if options.ring_time == -1:
				self.__message_flow["ring"]["result"] = True
			if options.answer_time == -1:
				self.__message_flow["answer"]["result"] = True
			if options.hangup_time == -1:
				self.__message_flow["hangup"]["result"] = True
			pass

		def channel_event(self, event):
			event_name = event.getHeader("Event-Name")
			event_sub_name = event.getHeader("Event-Subclass")

			if event_name in ['CHANNEL_CREATE']:
				return self.channel_create(event)
			elif event_name in ['CHANNEL_HANGUP']:
				return self.channel_hangup(event)

		def channel_create(self, event):
			uuid = event.getHeader("unique-id")
			session_id = event.getHeader("variable_session_id")
			call_dir = event.getHeader("Caller-Direction")
			if call_dir in ['inbound']:
				caller_num = event.getHeader("Caller-Caller-ID-Number")
				callee_num = event.getHeader("Caller-Destination-Number")
				callee_num = callee_num.split(";rn=")[0] if ";rn=" in callee_num else ""
				if options.caller_num == caller_num and options.callee_num == callee_num:
					
					if options.is_call.lower() not in ['yes']:
						print("ERR :recv target call %s --> %s" % (caller_num, callee_num))
						self.__message_flow["recv call"]["result"] = False
						return "end"
					else:
						print("INFO:recv target call %s --> %s" % (caller_num, callee_num))

					self.__message_flow["recv call"]["result"] = True
					self.__call["uuid"] = uuid

					if options.ring_time != -1:
						print("INFO:send ring after %ds" % (options.ring_time))
						time.sleep(options.ring_time)
						self.esl().execute("ring_ready", "", uuid)
						#self.esl().execute("playback", "/usr/local/freeswitch/sounds/music/8000/suite-espanola-op-47-leyenda.wav", uuid)
						self.__message_flow["ring"]["result"] = True

					if options.answer_time != -1:
						print("INFO:send answer after %ds" % (options.answer_time))
						time.sleep(options.answer_time)
						self.esl().execute("answer", "", uuid)
						#self.esl().execute("playback", "/usr/local/freeswitch/sounds/music/8000/suite-espanola-op-47-leyenda.wav", uuid)
						self.__message_flow["answer"]["result"] = True

					if options.hangup_time != -1:
						print("INFO:send hangup after %ds" % (options.hangup_time))
						time.sleep(options.hangup_time)
						self.esl().execute("hangup", "", uuid)
						self.__message_flow["hangup"]["result"] = True
					
					return "end"

		def channel_hangup(self, event):
			uuid = event.getHeader("unique-id")
			session_id = event.getHeader("variable_session_id")
			if self.__call.get("uuid", "") == uuid:
				print("INFO:call hangup")
				self.__message_flow["hangup"]["result"] = True
				return "end"

		# 校验整个呼叫过程中的错误
		def complete_check(self):
			proc_describe = ""
			seq = sys.maxint
			for msg, context in self.__message_flow.items():
				if not context["result"] and context["sequence"] < seq:
					proc_describe = context["describe"]
			else:
				if proc_describe:
					print("ERR :process '%s' result is not OK" % (proc_describe))
					return False
				else:
					return True

	callee = CalleeEvent(options.host, options.port, options.password)
	callee.run(options.timeout)
	if callee.complete_check():
		print(0)
	else:
		print(1)



		