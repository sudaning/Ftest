#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
import os, sys
import subprocess 
import threading
import time

from treport import report, caseReport, caseProcReport
from neko import color_str, ProcBar

# yaml包
try:
	import yaml
except ImportError as err:
	if "No module named" in str(err):
		print(color_str("this script base on PyYaml, I will install it first, please wait a moment", "purple"))
		result = os.system("yum -y install python-pip && pip install --upgrade pip && pip install pyyaml")
		if 0 != result:
			print(color_str("sorry, there have some problems on auto-install PyYaml, please install it manually", "red"));
			sys.exit(result)
		else:
			import yaml

# 解析配置脚本中能执行脚本的配置项参数
class caseCmd:
	"""
	every script except header context including two items that 'action' and 'description'. 
	this class manager that struct and parse its parameters like '%father_param.child_prarm' in 'action' line 
	"""
	def __init__(self, cmd, cmd_file):
		self.__cmd_file = cmd_file
		try:
			self.__action = cmd.get('action', {})
			self.__description = (cmd.get('description', "") or "[default]")
		except Exception as err:
			raise SyntaxError, "config format is illegal, not find keywords 'action' or 'description' in " + self.__cmd_file

	def action(self):
		"""
		action specify the script what will do
		"""
		return self.__action

	def description(self):
		"""
		description just to show on your given
		"""
		return self.__description

	def __parse_param(self, param, config_dict):
		"""
		parse parameters like '%father_param.child_prarm', specially '%' means calculated, '.' means a hierarchical relation
		"""
		p = None
		param = param.strip()
		if param[0] == '%':
			try:
				for c in param[1:].split('.'):
					if p:
						p = p.get(c, None)
					else:
						p = config_dict.get(c, None)
					# 配置参数不存在
					if not p:
						raise SyntaxError, "parse cmd failed, parameter '" + param[1:] + "' not find in config file"
			except Exception as e:
				raise SyntaxError, "parse cmd failed, parameter '" + param[1:] + "' format is illegal"
		return p

	def parse(self, config_dict):
		"""
		parse the items 'script' and 'parameter' under 'action' 
		"""
		params = []
		try:
			# 把参数拆分出来(参数之间可能会有多个空格相隔结尾还有\n，去掉这些分隔符)
			params.append(self.__action.get("script", "").strip() or "")
			parameter = self.__action.get("parameter", {}) or {}
		except Exception as err:
			raise SyntaxError, "config format is illegal, not find keywords 'script' or 'parameter' in " + self.__cmd_file

		for k, v in parameter.items():
			# 解析其中参数
			try:
				p = self.__parse_param(v, config_dict)
				# 脚本的参数约定以'--'作为长名字(长度大于1)，'-'作为短名字(长度为1)
				params.append(("-" if len(k.strip()) == 1 else "--") + k.strip() + " " + (str(p) if p else v.strip()))
			except Exception as e:
				raise Exception(e)
		else:
			return ' '.join(params)

class executeThread (threading.Thread):
	"""
	start a thread for script to execute 
	"""
	def __init__(self, threadID, name, d, timeout):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.d = d
		self.timeout = timeout

	def run(self):
		while self.timeout:
			try:
				# 等待子进程返回
				self.d['result'] = self.d['subproc'].communicate() 
				self.d['rep'].end_time("now")
				if self.d['result'] is not None:
					return
			except IOError as err:
				if err[0] == 11:
					time.sleep(1)
					self.timeout -= 1
					continue

class case:
	"""
	defined case features including:
	#. name        -- case name like 'SIPPHONE_V1.0.12_000001' (just show)
	#. description -- specify what's the case (just show)
	#. expection   -- specify expected result when the case done (just show)
	#. active      -- specify the case active or deactive (enable or not)
	#. check       -- stage 1 when the case running, check the environment is OK or not 
	#. setup       -- stage 2 when the case running, construct some essential data for the case 
	#. execute     -- stage 3 when the case running, testing a series of conditions in script
	#. teardown    -- stage 4 when the case running, recovery environment to before the case run
	"""

	__python_run = "/usr/bin/python"

	def __init__(self, case_file, context, config_dict, script_dir):
		self.__case_file = case_file
		self.__config_dict = config_dict
		self.__script_dir = script_dir

		self.__name = (context.get('name', '') or '[default]').strip('\n')
		self.__description = (context.get('description', '') or '[default]').strip('\n')
		self.__expection = (context.get('expection', '') or '[default]').strip('\n')
		self.__active = context.get('active', True)
		self.__check = context.get('check', [])
		self.__setup = context.get('setup', [])
		self.__execute = context.get('execute', [])
		self.__teardown = context.get('teardown', [])

	def __run_script_part(self, script, step, caserep, stage, silence, mod = "common"):
		"""
		parse a cmd and open a subprocess to execute script
		"""
		# 解析配置中action行的命令, 
		procrep = caseProcReport()
		caserep.add(procrep)
		#print(caserep, procrep)
		cmd = None
		try:
			cmd = caseCmd(script, self.__case_file)
			procrep.description(cmd.description())
			procrep.stage(stage)
			script_cmd = cmd.parse(self.__config_dict)
		except Exception as e:
			procrep.result(-1)
			procrep.details("ERR :" + str(e))
			print(color_str(str(e), 'red'))
			return False, cmd, procrep, None

		# 解析之后第一个必然是脚本的名字，后续的是参数
		c = script_cmd.split(' ')
		f = os.path.join(self.__script_dir, c[0])
		pargs = [self.__python_run, f] + c[1:] 
		
		# 提示开始测试了...
		procrep.script(f, ' '.join(c[1:]))

		if not silence and mod == "common":
			sys.stdout.write("PROCESS %02d " % step + cmd.description().encode('utf-8'))
		# 校验脚本是否存在
		if not os.path.exists(f):
			if not silence:
				print(color_str(" ... ERROR", 'red'))
				print("- details:")
				print(color_str("-- ERR :" + f + " not exists", 'red'))
			procrep.details("ERR :" + f + " not exists")
			return False, cmd, procrep, None

		# 开启子进程执行脚本
		procrep.isrun("yes")
		procrep.start_time("now")
		proc = subprocess.Popen(pargs, stdout=subprocess.PIPE)

		return True, cmd, procrep, proc

	def __run_common_script(self, script, step, caserep, stage, silence):
		"""
		open subprocess for every script to runing and then check&report them result
		note: the subprocess is blocking, scripts is serializable, running..done..running..done one by one
		"""
		if not script:
			return True, step

		step += 1

		for cnt, s in enumerate(script):
			
			# 执行脚本
			res, cmd, procrep, proc = self.__run_script_part(s, step + cnt, caserep, stage, silence)
			if not res:
				return False, step + cnt

			# 注意：此函数会等待子进程运行完成之后返回。若脚本有阻塞，这里会一直阻塞
			res = proc.communicate()
			procrep.end_time("now")
			# 约定检查脚本中最后一次输出0代表检查成功，之前的输出是脚本的运行过程
			if res is not None and res[0] is not None and '0' in res[0].split('\n')[-2:]:
				procrep.result(0)
				for detail in res[0].split('\n')[:-2]:
					procrep.details(detail)
				if not silence:
					print("... " + color_str("OK", 'green'))
			else:
				# 若执行失败，则输出脚本的执行过程
				procrep.result(1)
				if not silence:
					print("... " + color_str("ERROR", 'red'))
					print("- details:")
				for detail in res[0].split('\n')[:-2]:
					if not silence:
						print(color_str("-- " + detail, 'red' if 'ERR' in detail[:6] else 'sky_blue'))
					procrep.details(detail)
				return False, step + cnt

			# 尝试结束子进程
			try:
				proc.terminate()
			except Exception as err:
				pass
		else:
			return True, step + cnt

	# 运行'检查'脚本
	def __run_check(self, step, caserep, silence):
		"""
		run 'check' stage scripts
		"""
		return self.__run_common_script(self.__check, step, caserep, "check", silence)

	# 运行'初始化'脚本
	def __run_setup(self, step, caserep, silence):
		"""
		run 'setup' stage scripts
		"""
		return self.__run_common_script(self.__setup, step, caserep, "setup", silence)

	# 运行'执行'脚本
	def __run_execute(self, step, caserep, silence):
		"""
		run 'execute' stage scripts. specially, this stage can't blocking in a script, start thread to execute
		"""
		cases = []
		if not self.__execute:
			return True, step

		step += 1

		for cnt, s in enumerate(self.__execute):
			# 执行脚本
			res, cmd, procrep, proc = self.__run_script_part(s, step + cnt, caserep, "execute", silence, "exe")
			if not res:
				return False, step + cnt
			
 			# 开启线程等待脚本进程的返回
			d = {'result':None, 'subproc':proc, 'thread':None, 'cmd':cmd, 'rep':procrep}
			d['thread'] = executeThread(cnt, self.__name.encode('utf-8'), d, 3)
			d['thread'].start()
			cases.append(d)

			# 每个子进程之间执行间隔1秒
			time.sleep(1)
		else:
			# 等待所有线程结束(即子进程返回)
			for c in cases:
				c['thread'].join()

		# 报表
		for cnt, c in enumerate(cases):
			# 约定检查脚本中最后一次输出0代表检查成功
			res = c['result']
			if res is not None and res[0] is not None and '0' in res[0].split('\n')[-2:]:
				if not silence:
					print("PROCESS %02d " % (step + cnt) + c['cmd'].description().encode('utf-8') + "... " + color_str("OK", 'green'))
				c['rep'].result(0)
				#c['rep'].details("PROCESS %02d " % (step + cnt) + c['cmd'].description() + " OK")
				for detail in res[0].split('\n')[:-2]:
					c['rep'].details(detail)
				pass
			else:
				# 若执行失败，则输出脚本的执行过程
				c['rep'].result(1)

				if not silence:
					print("PROCESS %02d " % (step + cnt) + c['cmd'].description().encode('utf-8') + "... " + color_str("ERROR", 'red'))
					print("- details:")
				for detail in res[0].split('\n')[:-2]:
					if not silence:
						print(color_str("-- " + detail, 'red' if 'ERR' in detail else 'sky_blue'))
					c['rep'].details(detail)

			# 尝试结束子进程
			try:
				c['subproc'].terminate()
			except Exception as err:
				pass
		else:
			return True, cnt + step

	# 运行'卸载'脚本
	def __run_teardown(self, step, caserep, silence):
		"""
		run 'teardown' stage scripts
		"""
		return self.__run_common_script(self.__teardown, step, caserep, "teardown", silence)

	# 开始运行测试用例
	def run(self, cnt, caserep, silence):
		"""
		run scripts, you can type ctrl + c to terminate the long time process
		"""
		if not silence:
			print(color_str("\ncase" + str(cnt) + ": " + self.__name + " testing... ", "purple"))
			print(color_str("description: " + self.__description, "yellow"))
			print(color_str("expection  : " + self.__expection, "sky_blue"))

		try:
			# 报表收集信息开始
			caserep.name(self.__name)
			caserep.description(self.__description)
			caserep.expection(self.__expection)
			caserep.active(self.__active)
			caserep.start_time("now")

			# 开始运行脚本测试
			if self.__active:
				step = 0
				res, step = self.__run_check(step, caserep, silence)
				if res:# check成功才能进行setup
					res, step = self.__run_setup(step, caserep, silence)
					if res:# setup成功才能进行execute
						res, step = self.__run_execute(step, caserep, silence)
						# 只要setup成功，无论execute是否成功都应该teardown
						self.__run_teardown(step, caserep, silence)
			else:
				if not silence:
					print(color_str("active     : 否", "red"))

			# 报表收集信息结束
			caserep.end_time("now")
		except KeyboardInterrupt as err:
			sys.exit(1)
		
class caseMgr:
	"""
	manager the testing task
	"""
	def __init__(self, config_file, packet_file, script_dir, debug=False):
		self.__packet_file = packet_file
		self.__config_file = config_file
		self.__script_dir = script_dir
		self.__case = []
		self.__config = None
		self.__debug = debug

	def __load_config(self):
		"""
		load the variable config YAML file
		"""
		if self.__debug:
			print("load config")
		try:
			with open(self.__config_file) as f:
				self.__config = yaml.load(f)
				#print(self.__config)
				return True
		except Exception as e:
			print(color_str(str(e), "red"))
			return False

	def __load_case(self):
		"""
		load the case YAML file
		"""
		if self.__debug:
			print("load case")
		root = os.path.split(self.__packet_file)[0]
		try:
			with open(self.__packet_file) as f:
				p = yaml.load(f)

			# 配置中的包描述(删除YAML结构中的description和name，方便代码编写)
			packet_description = p.pop("description") if "description" in p else ""
			packet_name = p.pop("name") if "name" in p else ""

			if not p:
				return True

			# 遍历配置包中的测试套
			for suit_dir, suit_file_list in p.items(): 
				for suit_file in suit_file_list if suit_file_list else []:
					suit_path = os.path.join(root, suit_dir, suit_file)
					if not os.path.exists(suit_path):
						print(color_str("file " + suit_path + " is not exists", "yellow"))
						continue
					try:
						with open(suit_path) as f:
							s = yaml.load(f)
					except Exception as err:
						print(color_str(str(err), "red"))
						continue
					# 配置中的测试套描述
					suit_description = s.pop("description") if "description" in s else ""
					suit_name = s.pop("name") if "name" in s else ""
					if not s:
						continue
					# 遍历配置套中的测试用例
					for case_dir, case_file_list in s.items():
						for case_file in case_file_list if case_file_list else []:
							case_path = os.path.join(root, case_dir, case_file)
							if not os.path.exists(case_path):
								print(color_str("file " + case_path + " is not exists, please check file:" + suit_path, "yellow"))
								continue
							try:
								with open(case_path) as f:
									c = yaml.load(f)
							except Exception as err:
								print(color_str(str(err), "red"))
								continue
							#print(c)
							self.__case.append({"case": c, "case_path":case_path, \
								"suit_path":suit_path, "suit_description":suit_description, "suit_name":suit_name,\
								"packet_path":self.__packet_file, "packet_description":packet_description, "packet_name":packet_name,\
								})
			return True
		except Exception as e:
			print(color_str(str(e), "red"))
			return False
		

	def load(self):
		"""
		load the config&case YAML file
		"""
		return self.__load_config() and self.__load_case()

	def run(self, rep_mod, rep_dir, rep_success, silence):
		cnt = 0
		rep = report()
		rep.report_dir(rep_dir)
		rep.start_time("now")
		# 循环测试用例packet --> suit(s) --> case(s)
		cc = None
		total = sum([len(cc.get("case", {}) or {}) for cc in self.__case])
		
		s = color_str("total ", "purple") + color_str("%d" % total, "sky_blue") + color_str(" case(s) testing... ", "purple")
		if silence:
			p = ProcBar(mod='details').set_details(total, widget_type="count").start(s)
		else:
			print(s)

		for cc in self.__case:
			for c in cc.get("case", {}) or {}:
				cnt += 1
				caserep = caseReport(packet_path = self.__packet_file, suit_path = cc["suit_path"], case_path = cc["case_path"])
				case(cc["case_path"], c, self.__config, self.__script_dir).run(cnt, caserep, silence)
				rep.add(caserep)
				#print(rep, caserep)
				if silence:
					p.move()
		else:
			if silence:
				if cc:
					p.stop(color_str("OK", "green"))
				else:
					p.stop(color_str("WARNING (no cases run)", "yellow"))
					return

			# 生成报表
			s = color_str("\ngenerating report... ", "purple")
			if silence:
				p = ProcBar().start(s)
			else:
				print(s)

			rep.name(cc["packet_name"])
			rep.description(cc["packet_description"])
			rep.end_time("now")
			rep.generation(rep_mod, rep_success, silence)
			rep.mail(self.__config, silence)

			s = color_str("OK", "green")
			if silence:
				p.stop(s)
			
			total, success, success_list, failed, failed_list, error, error_list, unactive, unactive_list = rep.statistics()
			
			print(color_str("\n统计"))
			print(color_str("==============="))
			print(color_str(" 成功   : %d" % success, "green" if success else "white"))
			print(color_str(" 失败   : %d" % failed, "red" if failed else "white"))
			print(color_str(" 错误   : %d" % error, "red" if error else "white"))
			print(color_str(" 未激活 : %d" % unactive, "red" if unactive else "white"))
			print(color_str("---------------"))
			print(color_str(" 总计 : %d" % total, "sky_blue"))