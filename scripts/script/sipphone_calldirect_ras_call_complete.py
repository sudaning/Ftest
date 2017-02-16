#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

# 
#
#
#
#

import os,sys

if __name__ == '__main__':

	from optparse import OptionParser
	parser = OptionParser()
	parser.add_option('--host', dest='host')
	parser.add_option('--port', dest='port')
	parser.add_option('--password', dest='password')
	
	parser.add_option('--mysql_host', dest='mysql_host')
	parser.add_option('--mysql_port', dest='mysql_port', type='int')
	parser.add_option('--mysql_user', dest='mysql_user')
	parser.add_option('--mysql_password', dest='mysql_password')
	parser.add_option('--mysql_dbname', dest='mysql_dbname')

	parser.add_option('--lib', dest='lib', default='../lib')

	parser.add_option('--sipp_num', dest='sipp_num')
	parser.add_option('--callee_num', dest='callee_num')
	parser.add_option('--dis_num', dest='dis_num')
	parser.add_option('--accountid', dest='accountid')
	parser.add_option('--appid', dest='appid')
	parser.add_option('--record', dest='record', type='int')
	parser.add_option('--reason_code', dest='reason_code', type='int', default=0)
	parser.add_option('--hangup_dir', dest='hangup_dir')
	parser.add_option('--callee_sipp', dest='callee_sipp')

	parser.add_option('--timeout', dest='timeout', type='int', default=15)

	(options, args) = parser.parse_args()
	
	run_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
	sys.path.append(os.path.join(run_path, options.lib))
	from neko import ESLEvent
	class Event(ESLEvent):
		
		__bus_code = "05" # SIPPHONE的业务码
		__global_RecordUrl = "RecordUrl" # 录音URL的根路径RAS配置

		def __init__(self, ip, port, password):
			ESLEvent.__init__(self, ip, port, password)
			self.__A = {}
			self.__B = {}
			self.__message_flow = {\
				"recv A": {"sequence": 10, "result": False, "describe": "recv A calling"},
				"send B": {"sequence": 20, "result": False, "describe": "send B call"},
				"check RN": {"sequence": 30, "result": False, "describe": "check rn"},
				"check billing": {"sequence": 40, "result": False, "describe": "check billing"},
				"ring": {"sequence": 100, "result": False, "describe": "ring"},
				"answer": {"sequence": 200, "result": False, "describe": "answer"},
				"hangup": {"sequence": 300, "result": False, "describe": "hangup"},
				"hangup_ntf": {"sequence": 400, "result": False, "describe": "hangup notify"},
			}

			# 有错误原因
			if options.reason_code != 0:
				self.__message_flow['send B']['result'] = True
				self.__message_flow['check RN']['result'] = True
				self.__message_flow['ring']['result'] = True
				self.__message_flow['answer']['result'] = True
				self.__message_flow['hangup_ntf']['result'] = True

		def __get_rn(self, bus_code, appid, caller, callee):
			try:
				from number import Rn
				rn = Rn(options.mysql_host, options.mysql_port, options.mysql_user, options.mysql_password, options.mysql_dbname)
				return rn.get(bus_code, appid, caller, callee)
			except Exception as err:
				return err

		def __check_billing(self, test_billing):
			#"33e9;MASK!C!63348e574ff14cf484fcfeb137e38be8!!MTEzZDk4MzA0ZmUwMGQzMzdkYTkzNGYx!1!18682099276!075522453654!18589034543!075522453654!0!20161128115204"			
			b = test_billing[1:-1].split('!')
			if b[0] != "33e9;SIPPOUT":
				print("ERR :billing check failed... test:%s ref:%s" % (b[0], "33e9;SIPPOUT"))
				return False

			if b[1] != "C":
				print("ERR :billing check failed... test:%s ref:%s" % (b[1], "C"))
				return False

			# APPID
			if b[2] != options.appid:
				print("ERR :billing appid check failed... test:%s ref:%s" % (b[2], options.appid))
				return False

			# Acall SIP Call-ID: 截断成32位
			if b[4] != self.__A['sip_call_id'][:32]:
				print("ERR :billing sip Call-ID check failed... test:%s ref:%s" % (b[4], self.__A['sip_call_id'][:32]))
				return False

			# 录音标识(和配置的一样)
			if b[5] != str(options.record):
				print("ERR :billing record check failed... test:%s ref:%s" % (b[5], options.record))
				return False

			# 主叫号码(SIPPhone号码)
			if b[6] != options.sipp_num:
				print("ERR :billing sipphone number check failed... test:%s ref:%s" % (b[6], options.sipp_num))
				return False
			
			# 主叫显号(无)
			if b[7]:
				pass

			# 被叫号码(B号码)
			if b[8] != options.callee_num:
				print("ERR :billing callee number check failed... test:%s ref:%s" % (b[8], options.callee_num))
				return False

			# 被叫显号(显号)
			if b[9] != options.dis_num:
				print("ERR :billing display number check failed... test:%s ref:%s" % (b[9], options.dis_num))
				return False

			# 呼叫状态(成功/失败)
			ref = options.reason_code == 107003 and "1" or \
				options.reason_code == 107004 and "1" or \
				options.reason_code == 107005 and "6" or \
				options.reason_code == 107006 and "4" or \
				options.reason_code == 107007 and "5" or \
				options.reason_code == 107008 and "6" or \
				"0"
			if b[10] != ref:
				print("ERR :billing call status check failed... test:%s ref:%s" % (b[10], ref))
				return False

			# 录音时间
			self.__B['call_time'] = b[11]
			#print("INFO:billing call(record) time:%s" % (b[11]))

			# 呼叫次数
			if b[12] != "1":
				print("ERR :billing call counter check failed... test:%s ref:%s" % (b[12], "1"))
				return False

			# SIPPHONE呼叫用户情况(SIPPHONE禁用下，被叫用户状态无法判断)
			ref = options.reason_code in [107005, 107008] and "0" or \
				options.callee_sipp == "yes" and "3" or "1"
			if b[13] != ref:
				print("ERR :billing user type check failed... test:%s ref:%s" % (b[13], ref))
				return False

			# 中继ID
			#print("INFO:billing trunk id:%s" % (b[14]))
				
			return True

		def channel_event(self, event):
			event_name = event.getHeader("Event-Name")
			event_sub_name = event.getHeader("Event-Subclass")

			if event_name in ['CHANNEL_CREATE']:
				return self.channel_create(event)
			elif event_name in ['CHANNEL_PROGRESS']:
				return self.channel_progress(event)
			elif event_name in ['CHANNEL_PROGRESS_MEDIA']:
				return self.channel_progress_media(event)
			elif event_name in ['CHANNEL_ANSWER']:
				return self.channel_answer(event)
			elif event_name in ['CHANNEL_HANGUP']:
				return self.channel_hangup(event)
			elif event_name in ['RECORD_STOP']:
				return self.record_stop(event)
			elif event_name in ['CUSTOM']:
				if event_sub_name in ['sippout::hangup']:
					return self.custom_sippout_hangup(event)	

		def channel_create(self, event):
			uuid = event.getHeader("unique-id")
			session_id = event.getHeader("variable_session_id")
			call_dir = event.getHeader("Caller-Direction")
			sip_call_id = event.getHeader("variable_sip_call_id")

			if call_dir in ['inbound']:
				caller_num = event.getHeader("Caller-Caller-ID-Number")
				callee_num = event.getHeader("Caller-Destination-Number")

				# 检查入呼的主被叫号码
				if caller_num == options.sipp_num and callee_num == options.callee_num:
					# 是本次测试的呼叫
					self.__A['uuid'] = uuid
					self.__A['caller_num'] = caller_num
					self.__A['callee_num'] = callee_num
					self.__A['sip_call_id'] = sip_call_id
					print("INFO:locking A call success. uuid:%s, caller:%s, callee:%s" % (uuid, caller_num, callee_num))
					self.__message_flow["recv A"]["result"] = True
			elif call_dir in ['outbound']:
				uuid_other = event.getHeader("Other-Leg-Unique-ID")
				caller_num = event.getHeader("Caller-Caller-ID-Number")
				callee_num = event.getHeader("Caller-Callee-ID-Number")
				# 检查被叫的主被叫号码(隐私回呼B路的主叫号码应该是隐私号，被叫号码是映射的B号码)，A路UUID应该满足条件
				if caller_num == options.dis_num and callee_num == options.callee_num and uuid_other == self.__A.get('uuid', None):
					#print(0)
					#return "end"
					self.__B['uuid'] = uuid
					self.__B['other_uuid'] = uuid_other
					self.__B['caller_num'] = caller_num
					self.__B['callee_num'] = callee_num
					self.__B['sip_call_id'] = sip_call_id
					self.__A['other_uuid'] = uuid
					print("INFO:matched B call success. uuid:%s, caller:%s, callee:%s" % (uuid, caller_num, callee_num))
					self.__message_flow["send B"]["result"] = True
					
					# 检查RN是否生成正确
					test_rn = event.getHeader("variable_sip_invite_tel_params")
					if test_rn:
						test_rn = test_rn[3:] # 去掉'rn='字符串
						self.__B['rn'] = test_rn
						ref_rn = self.__get_rn(self.__bus_code, options.appid, caller_num, callee_num)
						if ref_rn != test_rn:
							print("ERR :check RN failed... test_rn:%s, ref_rn:%s, bus_code:%s, appid:%s" % 
								(test_rn, ref_rn, self.__bus_code, options.appid))
							return "end"
						else:
							print("INFO:check RN success. rn:%s" % (ref_rn))
							self.__message_flow["check RN"]["result"] = True
					else:
						print("ERR :not find RN from header:variable_sip_invite_tel_params")
						return "end"

					# 校验计费字段
					test_billing = event.getHeader("variable_sip_h_P-Access-Network-Info")
					if test_billing:
						self.__B['billing'] = test_billing
						success = self.__check_billing(test_billing)
						if not success:
							return "end"
						else:
							print("INFO:check billing success. billing:%s" % (test_billing))
							self.__message_flow["check billing"]["result"] = True
					else:
						print("ERR :not find billing from header:variable_sip_h_P-Access-Network-Info")
						return "end"

			pass 

		def channel_progress(self, event):
			uuid = event.getHeader("unique-id")
			session_id = event.getHeader("variable_session_id")

			if options.reason_code:
				if uuid != self.__A.get('uuid', None):
					return

				test_billing = event.getHeader("variable_P-Access-Network-Info") or event.getHeader("variable_sip_h_P-Access-Network-Info")
				if test_billing:
					self.__B['billing'] = test_billing
					success = self.__check_billing(test_billing)
					if not success:
						return "end"
					else:
						print("INFO:check billing success. billing:%s" % (test_billing))
						self.__message_flow["check billing"]["result"] = True
				else:
					print("ERR :not find billing from header:variable_P-Access-Network-Info")
					return "end"
			else:
				if uuid != self.__B.get('uuid', None):
					return
				
			print("INFO:ring success")
			self.__message_flow["ring"]["result"] = True
			
		def channel_progress_media(self, event):
			uuid = event.getHeader("unique-id")
			session_id = event.getHeader("variable_session_id")

			if uuid != self.__B.get('uuid', None):
				return

			print("INFO:ring(media) success")
			self.__message_flow["ring"]["result"] = True

		def channel_answer(self, event):
			uuid = event.getHeader("unique-id")
			session_id = event.getHeader("variable_session_id")

			if uuid != self.__B.get('uuid', None):
				return

			print("INFO:answer success")
			self.__message_flow["answer"]["result"] = True

		def channel_hangup(self, event):
			uuid = event.getHeader("unique-id")
			session_id = event.getHeader("variable_session_id")

			# 有原因码，则是A挂断，没有，则是B
			if options.reason_code:
				if uuid != self.__A.get('uuid', None):
					return
			else:
				if uuid != self.__B.get('uuid', None):
					return 

			reason = event.getHeader("variable_P-ras-reason")
			if reason and str(options.reason_code) != reason:
				print("ERR :hangup failed. reason:%s is not %s" % (reason, options.reason_code))
				return "end"

			print("INFO:hangup success. reason:%s" % (reason))
			self.__message_flow["hangup"]["result"] = True

			if options.reason_code:
				return "end"
				
		def record_stop(self, event):
			uuid = event.getHeader("unique-id")
			session_id = event.getHeader("variable_session_id")	

			if uuid != self.__A.get('uuid', None) and uuid != self.__B.get('uuid', None):
				return

			if not options.record:
				print("ERR : this case is not need record")
				print(1)
				return "end"

			# 检查是否有生成录音文件
			record_file_path = os.path.join('/'.join(event.getHeader("Record-File-Path").split('/')[:-1]), \
				"%s_%s_%s_%s_%s_CALLIN.wav" % (options.appid, options.sipp_num, options.callee_num, self.__A['sip_call_id'][:32], self.__B['call_time']))
			try:
				from pyssh import Ssh
				ssh = Ssh(options.host)
				stdin, stdout, stderr = ssh.exec_command('ls -l ' + record_file_path)
				if not stdout.readlines():
					print("ERR :check record file not exists. %s" % (record_file_path))
					print(1)
					return "end"
				else:
					print("INFO:check record file exists. %s" % (record_file_path))
			except Exception,err:
				print("ERR :" + str(err))
				print(1)
				return "end"

		def __check_hangup_notify(self, event):

			# SIP Call-ID
			if event.getHeader("variable_callSid") != self.__A['sip_call_id'][:32]:
				print("ERR :hangup notify Call-ID check failed... test:%s ref:%s" % (event.getHeader("variable_sip_call_id"), self.__A['sip_call_id']))
				return False

			# APPID
			if event.getHeader("variable_appId") != options.appid:
				print("ERR :hangup notify APPID check failed... test:%s ref:%s" % (event.getHeader("variable_appId"), options.appid))
				return False

			# 主叫号码
			if event.getHeader("variable_caller") != options.sipp_num:
				print("ERR :hangup notify caller number check failed... test:%s ref:%s" % (event.getHeader("variable_caller"), options.sipp_num))
				return False

			# 被叫号码
			if event.getHeader("variable_called") != options.callee_num:
				print("ERR :hangup notify callee number check failed... test:%s ref:%s" % (event.getHeader("variable_called"), options.callee_num))
				return False

			# 挂断方向
			hangup_dir = "0" if options.hangup_dir in ["caller"] else "1"

			if event.getHeader("variable_userFlag") != hangup_dir:
				print("ERR :hangup notify hangup dir check failed... test:%s ref:%s" % (event.getHeader("variable_userFlag"), hangup_dir))
				return False

			# 录音
			if options.record and self.__message_flow["answer"]["result"]:
				test_url = event.getHeader("variable_recordUrl")
				data = self.esl().api("global_getvar", self.__global_RecordUrl)
				if not test_url or not data:
					print("ERR :hangup notify not find test url or record url path...")
					return False
				else:
					record_url_path = data.getBody()
					# URL的时间只精确到小时20161216143520 --> 2016121614
					ref_url = os.path.join(record_url_path, options.accountid, options.appid, self.__B['call_time'][:10], 
						"%s_%s_%s_CALLIN.mp3" % (options.sipp_num, options.callee_num, self.__A['sip_call_id'][:32]))
					if test_url != ref_url:
						print("ERR :hangup notify hidden number check failed... test:%s ref:%s" % (test_url, ref_url))
						return False

			# 通话开始时间
			start_time = event.getHeader("variable_startTime")
			if not options.reason_code and not start_time or start_time == "0":
				print("ERR :hangup notify start time check failed... time:" + start_time if start_time else "")
				return False

			# 通话结束时间
			end_time = event.getHeader("variable_endTime")
			if not end_time or end_time == "0":
				print("ERR :hangup notify end time check failed... time:" + end_time if end_time else "")
				return False

			# 通话持续时长
			duration_time = event.getHeader("variable_duration")
			if not options.reason_code and not duration_time and int(duration_time) <= 0:
				print("ERR :hangup notify duration time check failed... time:" + duration_time)
				return False

			hangup_cause = event.getHeader("variable_sip_hangup_cause")

			return True

		def custom_sippout_hangup(self, event):
			uuid = event.getHeader("unique-id")
			session_id = event.getHeader("variable_session_id")
			sip_call_id = event.getHeader("variable_callSid")

			print("INFO: custom_sippout_hangup %s %s", (sip_call_id[:32], self.__A['sip_call_id'][:32]))
			if uuid != self.__A.get('uuid', None) and uuid != self.__B.get('uuid', None) and sip_call_id[:32] != self.__A['sip_call_id'][:32]:
				return 

			success = self.__check_hangup_notify(event)
			if not success:
				return "end"

			print("INFO:hangup notify success")
			self.__message_flow["hangup_ntf"]["result"] = True

			# 不录音，这将是最后一个消息
			if not options.record:
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

	sipphone = Event(options.host, options.port, options.password)
	sipphone.run(options.timeout)
	if sipphone.complete_check():
		print(0)
	else:
		print(1)

