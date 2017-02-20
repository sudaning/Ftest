#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
import os, sys
from optparse import OptionParser
from datetime import datetime
from neko import color_str, ProcBar

try:
	import xlwt
except ImportError as err:
	if "No module named" in str(err):
		print(color_str("this script base on xlwt, I will install it first, please wait a moment", "purple"))
		result = os.system("yum -y install python-pip && pip install --upgrade pip && pip install xlwt")
		if 0 != result:
			print(color_str("sorry, there have some problems on auto-install PyYaml, please install it manually", "red"));
			sys.exit(result)
		else:
			import xlwt

def beauty_path(p):
	ps = p.split("/")
	while True:
		l = [i for i,x in enumerate(ps) if x == ".."]
		if l and l[0] >= 1 and ps[l[0] - 1] != '.':
			del ps[l[0] - 1], ps[l[0] - 1]
		else:
			break
	return "/".join(ps)

# 测试管理、测试用例、测试过程类的通用特性
class repComm:

	def __init__(self, name = "", description = "", expection = ""):
		self.__name = name # 名字
		self.__description = description # 描述
		self.__expection = expection # 预期
		self.__start_time = None
		self.__end_time = None

	def name(self, name=""):
		if name:
			self.__name = name
		else:
			return self.__name

	def description(self, des=""):
		if des:
			self.__description = des
		else:
			return self.__description

	def expection(self, exp=""):
		if exp:
			self.__expection = exp
		else:
			return self.__expection

	def start_time(self, t = "get", format = "%Y-%m-%d %H:%M:%S"):
		if t == "now":
			self.__start_time = datetime.now()
		else:
			return self.__start_time.strftime(format) if self.__start_time else ""

	def end_time(self, t = "get", format = "%Y-%m-%d %H:%M:%S"):
		if t == "now":
			self.__end_time = datetime.now()
		else:
			return self.__end_time.strftime('%Y-%m-%d %H:%M:%S') if self.__end_time else ""

	def duration_time(self):
		if not self.__end_time or not self.__start_time:
			return ""
		else:
			# t = self.__end_time - self.__start_time
			# ms = t.microseconds / 1000
			# s = t.seconds % 60
			# m = t.seconds / 60
			# t_str = ((str(m) + "m") if m else "") + ((str(s) + "s") if s else "") + ((str(ms) + "ms") if ms else "")
			# return t_str
			return str(self.__end_time - self.__start_time)


# 用例报告类管理测试用例任务的一个执行过程
class caseProcReport(repComm):

	def __init__(self, description = "", stage = ""):
		
		self.__stage = stage # 所属阶段
		self.__script = "" # 执行脚本
		self.__script_argv = "" # 执行脚本参数
		self.__isrun = "no" # 是否有执行
		self.__result = -1 # 执行结果
		self.__details = "" # 执行详细信息
		repComm.__init__(self, description = description)
		
	def stage(self, st=""):
		if st:
			self.__stage = st
		else:
			return self.__stage

	def script(self, script="", argv=""):
		if script:
			self.__script = beauty_path(script)
			self.__script_argv = argv
		else:
			return self.__script, self.__script_argv

	def isrun(self, run = ""):
		if run.lower() in ["yes", "no"]:
			self.__isrun = run.lower()
		else:
			return self.__isrun

	def result(self, result=sys.maxint):
		if result != sys.maxint:
			self.__result = result
		else:
			return self.__result

	def details(self, det = ""):
		if det:
			self.__details += det + "\n"
		else:
			return self.__details

	
# 报告类管理一个测试用例，其中包含多个测试用例的执行过程
class caseReport(repComm):

	def __init__(self, name="", description="", packet_path="", suit_path="", case_path=""):
		self.__packet_path = beauty_path(packet_path) # 所属packet
		self.__suit_path = beauty_path(suit_path) # 所属suit
		self.__case_path = beauty_path(case_path) # 所属case
		self.__proc_list = [] # 执行过程列表
		self.__active = True
		repComm.__init__(self, name = name, description = description)

	def packet_path(self, p=""):
		if p:
			self.__packet_path = beauty_path(p)
		else:
			return self.__packet_path

	def suit_path(self, p=""):
		if p:
			self.__suit_path = beauty_path(p)
		else:
			return self.__suit_path

	def case_path(self, p=""):
		if p:
			self.__case_path = beauty_path(p)
		else:
			return self.__case_path

	# 添加一个casePorcReport的数据类
	def add(self, proc):
		#print("append ", self, proc)
		self.__proc_list.append(proc)

	def active(self, act="default"):
		if act == "default":
			return self.__active
		else:
			self.__active = act

	def procs(self):
		return self.__proc_list

# 报告管理类管理一个测试任务，其中包含多个测试用例
class report(repComm):

	def __init__(self, name="", description="", expection="", conf = None):
		self.__case_list = [] # 测试用例列表
		self.__report_dir = ""
		self.__rep_xls_file = ""
		self.__rep_xml_file = ""
		self.__conf = conf

		self.__language = conf.get("report", {}).get("language", "Chinese") if conf else "Chinese"

		repComm.__init__(self, name=name, description=description, expection=expection)

		self.__summary_title = self.__language == 'Chinese' and "测试报告" or "TEST REPORT"

		self.__summary_subtitle_abstract = self.__language == 'Chinese' and "简介" or "Abstract"
		self.__summary_subtitle_abstract_name = self.__language == 'Chinese' and "名字" or "Name"
		self.__summary_subtitle_abstract_description = self.__language == 'Chinese' and "描述" or "Description"

		self.__summary_subtitle_period = self.__language == 'Chinese' and "时间" or "Period"
		self.__summary_subtitle_period_from = self.__language == 'Chinese' and "开始" or "From"
		self.__summary_subtitle_period_to = self.__language == 'Chinese' and "结束" or "To"
		self.__summary_subtitle_period_duration = self.__language == 'Chinese' and "耗时" or "Duration"
		
		self.__summary_subtitle_schedule = self.__language == 'Chinese' and "计划" or "Schedule"
		self.__summary_subtitle_schedule_suit = self.__language == 'Chinese' and "组(套)" or "Suit"
		self.__summary_subtitle_schedule_case = self.__language == 'Chinese' and "活动" or "Case"
		self.__summary_subtitle_schedule_task = self.__language == 'Chinese' and "用例" or "Task"
		self.__summary_subtitle_schedule_script = self.__language == 'Chinese' and "脚本" or "Script"

		self.__summary_subtitle_result = self.__language == 'Chinese' and "结果" or "Result"
		self.__summary_subtitle_result_passed = self.__language == 'Chinese' and "通过" or "Passed"
		self.__summary_subtitle_result_failed = self.__language == 'Chinese' and "失败" or "Failed"
		self.__summary_subtitle_result_error = self.__language == 'Chinese' and "错误" or "Error"
		self.__summary_subtitle_result_unactive = self.__language == 'Chinese' and "未激活" or "Unactive"
		self.__summary_subtitle_result_total = self.__language == 'Chinese' and "总计" or "Total"
		
		self.__summary_subtitle_signature = self.__language == 'Chinese' and "来自遥远星星的自动化测试程序" or "The auto-test from other planet"

		self.__sheet_subtitle_abstract = self.__language == 'Chinese' and "简介" or "Abstract"
		self.__sheet_subtitle_abstract_name = self.__language == 'Chinese' and "名字" or "Name"
		self.__sheet_subtitle_abstract_description = self.__language == 'Chinese' and "描述" or "Description"
		self.__sheet_subtitle_abstract_expection = self.__language == 'Chinese' and "预期" or "Expection"
		self.__sheet_subtitle_abstract_config = self.__language == 'Chinese' and "所属配置" or "Config"
		self.__sheet_subtitle_abstract_result = self.__language == 'Chinese' and "结果" or "Result"
		self.__sheet_subtitle_abstract_result_passed = self.__language == 'Chinese' and "通过" or "Passed"
		self.__sheet_subtitle_abstract_result_failed = self.__language == 'Chinese' and "失败" or "Failed"
		self.__sheet_subtitle_abstract_result_unactive = self.__language == 'Chinese' and "未激活" or "Unactive"

		self.__sheet_subtitle_period = self.__language == 'Chinese' and "时间" or "Period"
		self.__sheet_subtitle_period_from = self.__language == 'Chinese' and "开始" or "From"
		self.__sheet_subtitle_period_to = self.__language == 'Chinese' and "结束" or "To"
		self.__sheet_subtitle_period_duration = self.__language == 'Chinese' and "耗时" or "Duration"

		self.__sheet_subtitle_detail = self.__language == 'Chinese' and "详情" or "Details"
		self.__sheet_subtitle_detail_stage = self.__language == 'Chinese' and "阶段" or "Stage"
		self.__sheet_subtitle_detail_index = self.__language == 'Chinese' and "序号" or "Index"
		self.__sheet_subtitle_detail_result = self.__language == 'Chinese' and "结果" or "Result"
		self.__sheet_subtitle_detail_result_success = self.__language == 'Chinese' and "成功" or "Success"
		self.__sheet_subtitle_detail_result_failed = self.__language == 'Chinese' and "失败" or "Failed"
		self.__sheet_subtitle_detail_description = self.__language == 'Chinese' and "描述" or "Description"
		self.__sheet_subtitle_detail_start_time = self.__language == 'Chinese' and "开始时间" or "Start Time"
		self.__sheet_subtitle_detail_end_time = self.__language == 'Chinese' and "结束时间" or "End Time"
		self.__sheet_subtitle_detail_duration = self.__language == 'Chinese' and "耗时" or "Duration"
		self.__sheet_subtitle_detail_script = self.__language == 'Chinese' and "运行脚本" or "Script Running"
		self.__sheet_subtitle_detail_detail = self.__language == 'Chinese' and "详细过程" or "Details"


	# 语言
	def language(self, l=''):
		if l:
			self.__language = l
		else:
			return self.__language

	# ‘阶段’翻译
	def stage(self, s):
		if self.language() == 'Chinese':
			return s == "check" and "检查" or \
				s == "setup" and "初始化" or \
				s == "execute" and "执行" or \
				s == "teardown" and "清理" or ""
		else:
			return s

	# 添加一个caseReport的数据类
	def add(self, case):
		self.__case_list.append(case)

	# 生成报告的目录
	def report_dir(self, p=""):
		if p:
			self.__report_dir = beauty_path(p)
			if not os.path.exists(self.__report_dir):
				try:
					os.mkdir(self.__report_dir)
				except Exception as err:
					raise Exception(err)
		else:
			return self.__report_dir

	# 统计用例执行情况
	def statistics(self):
		success = 0
		success_list = []
		failed = 0
		failed_list = []
		error = 0 
		error_list = []
		unactive = 0
		unactive_list = []
		for c in self.__case_list:
			res = -1
			for p in c.procs():
				if p.result() != 0:
					res = p.result()
					break
				else:
					res = 0
			if res == 0:
				success += 1
				success_list.append(c.name())
			elif res == 1:
				failed += 1
				failed_list.append(c.name())
			elif res == -1:
				unactive += 1
			else:
				error += 1
				error_list.append(c.name())
		return success + failed + error + unactive, success, success_list, failed, failed_list, error, error_list, unactive, unactive_list

	# XML形式报告
	def __rep_xml(self):
		pass

	# DEBUG形式报告
	def __rep_debug(self):
		
		# 总体描述
		print("\nTest Task '" + self.name() + "' duration:" + self.duration_time() + " from " + self.start_time() + " to " + self.end_time())

		# 统计执行总体情况
		total, success, success_list, failed, failed_list, error, error_list, unactive, unactive_list = self.statistics()

		print("{0:^20}".format("success") + "{0:^20}".format("failed") + "{0:^20}".format("error") + "{0:^20}".format("total"))
		print("{0:^20}".format(success) + "{0:^20}".format(failed) + "{0:^20}".format(error) + "{0:^20}".format(total))
		return
		for case in self.__case_list:
			print(case.name()) # 测试用例名字
			print(case.description()) # 测试描述
			print(case.packet_path() + " --> " + case.suit_path() + " --> " + case.case_path()) # 测试的来源路径
			print(case.start_time() + " --> " + case.end_time()) # 测试起止时间
			print("--------------")
			for proc in case.procs():
				print(proc.description()) # 测试过程描述
				print(proc.stage()) # 测试过程阶段
				print(proc.result()) # 测试结果
				print(proc.start_time() + " --> " + proc.end_time()) # 测试过程起止时间
				print(proc.script()) # 测试过程执行脚本
				print(proc.details()) # 测试过程详细信息
				print("###################")

	def __create_xls_sheet(self, wb, name):
		# 若重名则自动添加序号到页名后面
		sheet_name = name
		try_cnt = 1
		sheet = None
		while True:
			try:
				sheet = wb.add_sheet(sheet_name, cell_overwrite_ok=True) #创建详情页
			except Exception as err:
				if 'duplicate worksheet' in str(err):
					sheet_name = "%s(%d)" % (name, try_cnt)
					try_cnt += 1
					continue
			else:
				break
		return sheet

	def __rep_xls_summary(self, wb):
		borders_attr = "borders: top thin, bottom thin, left thin, right thin;"

		tittle_style = xlwt.easyxf('font: height 400, name Arial Black, colour_index blue, bold on; align: wrap off, vert centre, horiz centre;')
		subtittle_left_style = xlwt.easyxf('font: height 240, name Arial, colour_index gray40, bold off, italic on; align: wrap off, vert centre, horiz left;')
		subtittle_right_style = xlwt.easyxf('font: height 240, name Arial, colour_index gray40, bold off, italic on; align: wrap off, vert centre, horiz left;')
		subtittle_top_and_bottom_style = xlwt.easyxf('font: height 240, name Arial, colour_index gray40, bold off, italic on; align: wrap off, vert centre, horiz left;')
		blank_style = xlwt.easyxf('font: height 650, name Arial, colour_index brown, bold off; align: wrap off, vert centre, horiz left;')
		
		italic_style = xlwt.easyxf('font: height 240, name Arial, colour_index black, bold off, italic on; align: wrap off, vert centre, horiz left;')
		common_style = 'font: height 240, name Arial, colour_index black, bold off; align: wrap off, vert centre, horiz left;'
		normal_style = xlwt.easyxf(common_style + borders_attr)
		normal_red_style = xlwt.easyxf(common_style + borders_attr + 'pattern: pattern solid, pattern_fore_colour red;')
		normal_green_style = xlwt.easyxf(common_style + borders_attr + 'pattern: pattern solid, pattern_fore_colour bright_green;')
		normal_purple_style = xlwt.easyxf(common_style + borders_attr + 'pattern: pattern solid, pattern_fore_colour purple_ega;')
		normal_gray_style = xlwt.easyxf(common_style + borders_attr + 'pattern: pattern solid, pattern_fore_colour gray25;')

		item_tittle_style = xlwt.easyxf('font: height 300, name Arial Black, colour_index brown, bold on; align: wrap off, vert centre, horiz left;')
		item_style = xlwt.easyxf('font: height 240, name Arial, colour_index black, bold off; align: wrap off, vert centre, horiz left;''pattern: pattern solid, pattern_fore_colour gray40;' + borders_attr)
		sheet = self.__create_xls_sheet(wb, "summary") #创建总结页
		if not sheet:
			return
		
		# 列宽控制
		width = max(40, len(self.name()), len(self.description())) + 20
		for c in range(1, 2 + 1):
			sheet.col(c).width = 256 * (25 if c % 2 else width)

		# 位置控制
		start_row = 0
		start_col = 1
		end_col = 2
		interval_row = 1
		offset_row = 0
		
		# 标题
		sheet.write_merge(start_row + offset_row, start_row + offset_row, start_col, end_col, self.__summary_title, tittle_style)
		
		offset_row += 1
		sheet.write(start_row + interval_row + offset_row, start_col, self.__summary_subtitle_abstract, item_tittle_style)
		# 测试名
		offset_row += 1
		sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__summary_subtitle_abstract_name, item_style)
		sheet.write(start_row + interval_row + offset_row, start_col + 1, self.name(), normal_style)
		# 测试描述
		offset_row += 1
		sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__summary_subtitle_abstract_description, item_style)
		sheet.write(start_row + interval_row + offset_row, start_col + 1, self.description(), normal_style)
		
		# 测试时间
		offset_row += 2
		sheet.write(start_row + interval_row + offset_row, start_col, self.__summary_subtitle_period, item_tittle_style)
		offset_row += 1
		sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__summary_subtitle_period_from, item_style)
		sheet.write(start_row + interval_row + offset_row, start_col + 1, self.start_time(), normal_style)
		offset_row += 1
		sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__summary_subtitle_period_to, item_style)
		sheet.write(start_row + interval_row + offset_row, start_col + 1, self.end_time(), normal_style)
		offset_row += 1
		sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__summary_subtitle_period_duration, item_style)
		sheet.write(start_row + interval_row + offset_row, start_col + 1, self.duration_time(), normal_style)
		
		# 测试套、用例数、用例任务计划数
		offset_row += 2
		sheet.write(start_row + interval_row + offset_row, start_col, self.__summary_subtitle_schedule, item_tittle_style)

		# 测试套，packet下的suit.yaml
		offset_row += 1
		suit_cnt = len(set([case.suit_path() for case in self.__case_list]))
		sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__summary_subtitle_schedule_suit, item_style)
		sheet.write(start_row + interval_row + offset_row, start_col + 1, suit_cnt, normal_style)
		
		# 测试用例，suit下的case.yaml
		offset_row += 1
		case_cnt = len(set([case.case_path() for case in self.__case_list]))
		sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__summary_subtitle_schedule_case, item_style)
		sheet.write(start_row + interval_row + offset_row, start_col + 1, case_cnt, normal_style)

		# 测试任务，case.yaml下的项
		offset_row += 1
		sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__summary_subtitle_schedule_task, item_style)
		sheet.write(start_row + interval_row + offset_row, start_col + 1, len(self.__case_list), normal_style)
		
		# 测试脚本，case.yaml下项的脚本description,action对
		offset_row += 1
		script_cnt = sum([len([proc for proc in case.procs() if proc.isrun() == "yes"]) for case in self.__case_list])
		sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__summary_subtitle_schedule_script, item_style)
		sheet.write(start_row + interval_row + offset_row, start_col + 1, script_cnt, normal_style)

		# 结果汇总
		total, success, success_list, failed, failed_list, error, error_list, unactive, unactive_list = self.statistics()
		offset_row += 2
		sheet.write(start_row + interval_row + offset_row, start_col, self.__summary_subtitle_result, item_tittle_style)
		offset_row += 1
		sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__summary_subtitle_result_passed, item_style)
		sheet.write(start_row + interval_row + offset_row, start_col + 1, success, normal_green_style)
		#sheet.write(start_row + interval_row + offset_row, start_col + 2, " ".join(success_list), italic_style)
		offset_row += 1
		sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__summary_subtitle_result_failed, item_style)
		sheet.write(start_row + interval_row + offset_row, start_col + 1, failed, normal_red_style if failed else normal_style)
		sheet.write(start_row + interval_row + offset_row, start_col + 2, " ".join(failed_list), italic_style)
		offset_row += 1
		sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__summary_subtitle_result_error, item_style)
		sheet.write(start_row + interval_row + offset_row, start_col + 1, error, normal_red_style if error else normal_style)
		sheet.write(start_row + interval_row + offset_row, start_col + 2, " ".join(error_list), italic_style)
		offset_row += 1
		sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__summary_subtitle_result_unactive, item_style)
		sheet.write(start_row + interval_row + offset_row, start_col + 1, unactive, normal_gray_style if unactive else normal_style)
		sheet.write(start_row + interval_row + offset_row, start_col + 2, " ".join(unactive_list), italic_style)
		offset_row += 1
		sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__summary_subtitle_result_total, item_style)
		sheet.write(start_row + interval_row + offset_row, start_col + 1, total, normal_purple_style)

		return sheet

	def __rep_xls_details(self, summary_sheet, wb):

		for case in self.__case_list:

			result = all([proc.result() == 0 for proc in case.procs()])
			active = case.active()

			# 不报告成功的详情
			if not self.__rep_success and result and active:
				continue

			sheet = self.__create_xls_sheet(wb, case.name()) #创建详情页
			if not sheet:
				continue

			borders_attr = "borders: top thin, bottom thin, left thin, right thin;"

			tittle_style = xlwt.easyxf('font: height 400, name Arial Black, colour_index blue, bold on; align: wrap off, vert centre, horiz centre;')
			subtittle_left_style = xlwt.easyxf('font: height 240, name Arial, colour_index gray40, bold off, italic on; align: wrap off, vert centre, horiz left;')
			subtittle_right_style = xlwt.easyxf('font: height 240, name Arial, colour_index gray40, bold off, italic on; align: wrap off, vert centre, horiz left;')
			subtittle_top_and_bottom_style = xlwt.easyxf('font: height 240, name Arial, colour_index gray40, bold off, italic on; align: wrap off, vert centre, horiz left;')
			blank_style = xlwt.easyxf('font: height 650, name Arial, colour_index brown, bold off; align: wrap off, vert centre, horiz left;')
			
			common_style = 'font: height 240, name Arial, colour_index black, bold off; align: wrap off, vert centre, horiz left;' + borders_attr
			normal_style = xlwt.easyxf(common_style)
			normal_red_style = xlwt.easyxf(common_style + 'pattern: pattern solid, pattern_fore_colour red;')
			normal_green_style = xlwt.easyxf(common_style + 'pattern: pattern solid, pattern_fore_colour bright_green;')
			normal_purple_style = xlwt.easyxf(common_style + 'pattern: pattern solid, pattern_fore_colour purple_ega;')
			normal_gray_style = xlwt.easyxf(common_style + borders_attr + 'pattern: pattern solid, pattern_fore_colour gray25;')

			item_tittle_style = xlwt.easyxf('font: height 300, name Arial Black, colour_index brown, bold on; align: wrap off, vert centre, horiz left;')
			item_sub_tittle_style = xlwt.easyxf('font: height 240, name Arial Black, colour_index red, bold on; align: wrap off, vert centre, horiz left;')
			item_style = xlwt.easyxf('font: height 240, name Arial, colour_index black, bold off; align: wrap off, vert centre, horiz left;''pattern: pattern solid, pattern_fore_colour gray40;' + borders_attr)
			
			# 列宽控制
			for c in range(1, 10 + 1):
				if c in [2, 3]:
					sheet.col(c).width = 256 * 10
				elif c in [1]:
					sheet.col(c).width = 256 * 15
				elif c in [7]:
					sheet.col(c).width = 256 * 20
				elif c in [4, 9]:
					sheet.col(c).width = 256 * 50
				else:
					sheet.col(c).width = 256 * 25

			# 位置控制
			start_row = 0
			start_col = 1
			end_col = 2
			interval_row = 1
			offset_row = 0
			
			sheet.write(start_row + interval_row + offset_row, start_col, self.__sheet_subtitle_abstract, item_tittle_style)
			# 测试名
			offset_row += 1
			sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__sheet_subtitle_abstract_name, item_style)
			sheet.write_merge(start_row + interval_row + offset_row, start_row + interval_row + offset_row, start_col + 1, start_col + 4, case.name(), normal_style)
			# 测试描述
			offset_row += 1
			sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__sheet_subtitle_abstract_description, item_style)
			sheet.write_merge(start_row + interval_row + offset_row, start_row + interval_row + offset_row, start_col + 1, start_col + 4, case.description(), normal_style)
			# 预期结果
			offset_row += 1
			sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__sheet_subtitle_abstract_expection, item_style)
			sheet.write_merge(start_row + interval_row + offset_row, start_row + interval_row + offset_row, start_col + 1, start_col + 4, case.expection(), normal_style)
			# 测试配置
			offset_row += 1
			sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__sheet_subtitle_abstract_config, item_style)
			sheet.write_merge(start_row + interval_row + offset_row, start_row + interval_row + offset_row, start_col + 1, start_col + 4, case.case_path(), normal_style)
			# 测试结果
			offset_row += 1
			sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__sheet_subtitle_abstract_result, item_style)
			
			result_str = not active and self.__sheet_subtitle_abstract_result_unactive or (result and self.__sheet_subtitle_abstract_result_passed or self.__sheet_subtitle_abstract_result_failed)
			style = not active and normal_gray_style or (result and normal_green_style or normal_red_style)
			sheet.write_merge(start_row + interval_row + offset_row, start_row + interval_row + offset_row, start_col + 1, start_col + 4, result_str, style)

			# 没有激活的用例不输出时间和详情
			if not active:
				continue

			# 测试时间
			offset_row += 2
			sheet.write(start_row + interval_row + offset_row, start_col, self.__sheet_subtitle_period, item_tittle_style)
			offset_row += 1
			sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__sheet_subtitle_period_from, item_style)
			sheet.write_merge(start_row + interval_row + offset_row, start_row + interval_row + offset_row, start_col + 1, start_col + 4, case.start_time(), normal_style)
			offset_row += 1
			sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__sheet_subtitle_period_to, item_style)
			sheet.write_merge(start_row + interval_row + offset_row, start_row + interval_row + offset_row, start_col + 1, start_col + 4, case.end_time(), normal_style)
			offset_row += 1
			sheet.write(start_row + interval_row + offset_row, start_col + 0, self.__sheet_subtitle_period_duration, item_style)
			sheet.write_merge(start_row + interval_row + offset_row, start_row + interval_row + offset_row, start_col + 1, start_col + 4, case.duration_time(), normal_style)

			# 测试过程(任务)
			offset_row += 2
			sheet.write(start_row + interval_row + offset_row, start_col, self.__sheet_subtitle_detail, item_tittle_style)
			offset_row += 1
			
			# 标题
			stage_col = start_col + 0
			sheet.write(start_row + interval_row + offset_row, stage_col, self.__sheet_subtitle_detail_stage, item_style)
			sheet.write(start_row + interval_row + offset_row, start_col + 1, self.__sheet_subtitle_detail_index, item_style)
			sheet.write(start_row + interval_row + offset_row, start_col + 2, self.__sheet_subtitle_detail_result, item_style)
			sheet.write(start_row + interval_row + offset_row, start_col + 3, self.__sheet_subtitle_detail_description, item_style)
			sheet.write(start_row + interval_row + offset_row, start_col + 4, self.__sheet_subtitle_detail_start_time, item_style)
			sheet.write(start_row + interval_row + offset_row, start_col + 5, self.__sheet_subtitle_detail_end_time, item_style)
			sheet.write(start_row + interval_row + offset_row, start_col + 6, self.__sheet_subtitle_detail_duration, item_style)
			sheet.write(start_row + interval_row + offset_row, start_col + 7, self.__sheet_subtitle_detail_script, item_style)
			sheet.write(start_row + interval_row + offset_row, start_col + 8, self.__sheet_subtitle_detail_detail, item_style)
			
			# 内容
			stage_context = {}
			for cnt, proc in enumerate(case.procs()):
				offset_row += 1
				
				merge_len = 0
				if proc.details():
					details = proc.details().split('\n')[:-1]
					merge_len = len(details) - 1
					for detail_cnt, detail in enumerate(details):
						sheet.write(start_row + interval_row + offset_row + detail_cnt, start_col + 8, detail, normal_red_style if "ERR" in detail else normal_style)
				else:
					sheet.write(start_row + interval_row + offset_row, start_col + 8, proc.details(), normal_red_style if "ERR" in proc.details() else normal_style)

				c = stage_context.get(proc.stage(), None)
				if c is not None:
					c.append((start_row + interval_row + offset_row, start_row + interval_row + offset_row + merge_len))
				else:
					stage_context[proc.stage()] = [(start_row + interval_row + offset_row, start_row + interval_row + offset_row + merge_len)]
				#sheet.write_merge(start_row + interval_row + offset_row, start_row + interval_row + offset_row + merge_len, stage_col, stage_col, proc.stage(), normal_style)
				sheet.write_merge(start_row + interval_row + offset_row, start_row + interval_row + offset_row + merge_len, start_col + 1, start_col + 1, cnt + 1, normal_style)
				sheet.write_merge(start_row + interval_row + offset_row, start_row + interval_row + offset_row + merge_len, start_col + 2, start_col + 2, 
					self.__sheet_subtitle_detail_result_success if proc.result() == 0 else self.__sheet_subtitle_detail_result_failed, 
					normal_green_style if proc.result() == 0 else normal_red_style)
				sheet.write_merge(start_row + interval_row + offset_row, start_row + interval_row + offset_row + merge_len, start_col + 3, start_col + 3, proc.description(), normal_style)		
				sheet.write_merge(start_row + interval_row + offset_row, start_row + interval_row + offset_row + merge_len, start_col + 4, start_col + 4, proc.start_time(), normal_style)
				sheet.write_merge(start_row + interval_row + offset_row, start_row + interval_row + offset_row + merge_len, start_col + 5, start_col + 5, proc.end_time(), normal_style)
				sheet.write_merge(start_row + interval_row + offset_row, start_row + interval_row + offset_row + merge_len, start_col + 6, start_col + 6, proc.duration_time(), normal_style)
				sheet.write_merge(start_row + interval_row + offset_row, start_row + interval_row + offset_row + merge_len, start_col + 7, start_col + 7, " ".join(proc.script()), normal_style)

				offset_row += merge_len
			else:
				# 合并相同的stage
				#print(stage_context)
				merge_row_list = []
				for stage, row_list in stage_context.items():
					start, end = 0, 0 
					begin = True
					for row in row_list:
						if not begin:
							if end + 1 == row[0]:
								end = row[1]
							else:
								merge_row_list.append((start, end, stage))
								begin = True
						else:
							start, end = row[0], row[1]
							begin = False
					else:
						merge_row_list.append({"start":start, "end":end, "stage":stage})
				else:
					#print(merge_row_list)
					for merge_row in merge_row_list:
						sheet.write_merge(merge_row["start"], merge_row["end"], stage_col, stage_col, self.stage(merge_row["stage"]), normal_style)


	# XLS形式报告(excel)
	def __rep_xls(self):
		wb = xlwt.Workbook(encoding = 'utf-8') #创建工作簿

		summary_sheet = self.__rep_xls_summary(wb)
		self.__rep_xls_details(summary_sheet, wb)

		# 生成的文件名格式report_[测试任务名]_[开始时间].xls
		self.__rep_xls_file = os.path.join(self.report_dir() ,"report_" + self.name().encode('utf-8') + "_" + self.start_time(format = "%Y%m%d%H%M%S") + ".xls")
		wb.save(self.__rep_xls_file) #保存文件
		return self.__rep_xls_file

	def generation(self, mod, rep_success, silence):
		if not silence:
			p = ProcBar().start("REPORT 01 " + "%s '" % (self.__language == "Chinese" and "生成" or "generating") + mod + "' %s..." % (self.__language == "Chinese" and "报告" or "report"))
		self.__mod = mod
		self.__rep_success = rep_success
		if mod in ["xls"]:
			f = self.__rep_xls()
		elif mod in ["xml"]:
			f = self.__rep_xml()
		elif mod in ["debug"]:
			f = self.__rep_debug()
		else:
			f = self.__rep_xls()
		if not silence:
			p.stop(color_str("OK", "green") + " %s:" % (self.__language == "Chinese" and "路径" or "path") + f)

	def mail(self, silence):
		if not silence:
			p = ProcBar().start("REPORT 02 " + "%s..." % (self.__language == "Chinese" and "发送报告" or "send mail"))
		if self.__mod in ["xls"]:
			f = self.__rep_xls_file
		elif self.__mod in ["xml"]:
			f = self.__rep_xml_file
		else:
			return

		try:
			from email.mime.text import MIMEText
			from email.mime.multipart import MIMEMultipart
			from email.Header import Header
			import smtplib
		except ImportError as err:
			p.stop(color_str(str(err), "red"))
			return

		file_name = os.path.split(f)[-1]
		smtp = self.__conf.get("report", {}).get("sender", {}).get("smtp", "")
		sender = self.__conf.get("report", {}).get("sender", {}).get("from", "")
		user = self.__conf.get("report", {}).get("sender", {}).get("user", "")
		password = self.__conf.get("report", {}).get("sender", {}).get("password", "")
		delivers = self.__conf.get("report", {}).get("delivers", {})
		enable = self.__conf.get("report", {}).get("enable", "")

		if not smtp or not sender or not user or not password or not delivers:
			if not silence:
				p.stop(color_str("MISSING CONFIG PARAMETER", "red"))
			return 

		if not enable:
			if not silence:
				p.stop(color_str("DISABLE", "red"))
			return 

		#创建一个带附件的实例

		msg = MIMEMultipart()
		total, success, success_list, failed, failed_list, error, error_list, unactive, unactive_list = self.statistics()
		s = '<html>'
		s += '<head>'
		#s += '<style class="fox_global_style">div.fox_html_content { line-height: 1.5; }</style> '
		s += '</head>'
		s += '<body>'
		s += '<table width="99.99%" height="100%" style="padding: 10px; background-color: transparent;" border="0" cellpadding="0" cellspacing="0" background="file:///../res/bg.jpg"> '
		s += '<tbody>'
		s += '<tr> '
		s += '<td valign="top" style="width:100%;height:100%;"> '
		s += '<div id="divFMContentBody" contenteditable="true" style="min-height: 656px;"> '
		s += '<div style="font-size: 24px;">'
		s += '<br />'
		s += '</div>'
		s += '<div style="font-size: 27px;">'
		s += '<span style="font-family: 微软雅黑, Tahoma;"><b>%s</b></span>' % self.__summary_title
		s += '</div>'
		s += '<div style="font-size: 24px;">'
		s += '<br />'
		s += '</div>'
		s += '<div style="font-size: 24px;">'
		s += '<span style="font-family: 微软雅黑, Tahoma;"><font color="#993300"><b>%s</b></font></span>' % self.__summary_subtitle_abstract
		s += '</div>'
		s += '<div style="">'
		s += '<span style="background-color: rgba(0, 0, 0, 0); font-family: \'微软雅黑, Tahoma\'; font-size: 16px; line-height: 1.5;"></span>'
		s += '<font face="微软雅黑, Tahoma">{0}：{1}</font>'.format(self.__summary_subtitle_abstract_name, self.name())
		s += '</div>'
		s += '<div style="">'
		s += '<font face="微软雅黑, Tahoma">{0}：{1}</font>'.format(self.__summary_subtitle_abstract_description, self.description().encode('utf-8'))
		s += '</div>'
		s += '<div style="">'
		s += '<font face="微软雅黑, Tahoma"><br /></font>'
		s += '</div>'
		s += '<div style="">'
		s += '<font face="微软雅黑, Tahoma"><font><b style="color: rgb(153, 51, 0); font-size: x-large; line-height: 36px;">%s</b></font></font>' % self.__summary_subtitle_period
		s += '</div>'
		s += '<div style="">'
		s += '<font face="微软雅黑, Tahoma"><span style="line-height: 24px;"></span>{0}：{1}</font>'.format(self.__summary_subtitle_period_from, self.start_time())
		s += '</div>'
		s += '<div style="">'
		s += '<font face="微软雅黑, Tahoma"><span style="line-height: 24px;"></span>{0}：{1}</font>'.format(self.__summary_subtitle_period_to, self.end_time())
		s += '</div>'
		s += '<div style="">'
		s += '<font face="微软雅黑, Tahoma"><span style="line-height: 24px;"></span>{0}：{1}</font>'.format(self.__summary_subtitle_period_duration, self.duration_time())
		s += '</div>'
		s += '<div style="">'
		s += '<font face="微软雅黑, Tahoma"><br /></font>'
		s += '</div>'
		s += '<div style="">'
		s += '<span style="color: rgb(153, 51, 0); font-family: 微软雅黑, Tahoma; font-size: 24px;"><b>%s</b></span>' % self.__summary_subtitle_schedule
		s += '</div>'
		s += '<div style="">'
		s += '<font face="微软雅黑, Tahoma">{0}：{1}</font>'.format(self.__summary_subtitle_schedule_suit, len(set([case.suit_path() for case in self.__case_list])))
		s += '</div>'
		s += '<div style="">'
		s += '<font face="微软雅黑, Tahoma">{0}：{1}</font>'.format(self.__summary_subtitle_schedule_case,len(set([case.case_path() for case in self.__case_list])))
		s += '</div>'
		s += '<div style="">'
		s += '<font face="微软雅黑, Tahoma">{0}：{1}</font>'.format(self.__summary_subtitle_schedule_task,len(self.__case_list))
		s += '</div>'
		s += '<div style="">'
		s += '<font face="微软雅黑, Tahoma">{0}：{1}</font>'.format(self.__summary_subtitle_schedule_script, sum([len([proc for proc in case.procs() if proc.isrun() == "yes"]) for case in self.__case_list]))
		s += '</div>'
		s += '<div style="">'
		s += '<br />'
		s += '</div>'
		s += '<div style="">'
		s += '<font color="#993300" face="微软雅黑, Tahoma" size="5"><b>%s</b></font>' % self.__summary_subtitle_result
		s += '</div>'
		s += '<div style="font-size: 24px;">'
		s += '<table border="1" bordercolor="#000000" cellpadding="2" cellspacing="0" style="font-size: 10pt; border-collapse:collapse; border:none" width="50%"> '
		s += '<tbody>'

		s += '<tr> '
		s += '<td width="50%" style="border: solid 1 #000000" nowrap=""><font size="2">'
		s += '<div>'
		s += '<font face="Verdana"></font>'
		s += '<span style="font-family: 微软雅黑; background-color: transparent; line-height: 1.5;">%s</span>' % self.__summary_subtitle_result_passed
		s += '</div></font></td>'
		s += '<td width="50%" style="border: solid 1 #000000" nowrap=""><font face="微软雅黑">{0}</font></td> '.format(success)
		s += '</tr> '

		s += '<tr> '
		s += '<td width="50%" style="border: solid 1 #000000" nowrap="">'
		s += '<span style="font-family: 微软雅黑; font-size: 14px; line-height: 21px; white-space: normal;">%s</span></td>' % self.__summary_subtitle_result_failed
		s += '<td width="50%" style="border: solid 1 #000000" nowrap=""><font size="2" face="微软雅黑">'
		s += '<div>'
		s += '{0}'.format(failed)
		s += '</div></font></td> '
		s += '</tr> '

		s += '<tr> '
		s += '<td width="50%" style="border: solid 1 #000000" nowrap=""><font size="2" face="微软雅黑">'
		s += '<div>'
		s += '<span style="font-size: 14px; white-space: normal; background-color: transparent; line-height: 1.5;"></span>'
		s += '<span style="font-size: 14px; line-height: 21px; white-space: normal; background-color: transparent;">%s</span>' % self.__summary_subtitle_result_error
		s += '</div></font></td> '
		s += '<td width="50%" style="border: solid 1 #000000" nowrap=""><font size="2" face="微软雅黑">'
		s += '<div>'
		s += '{0}'.format(error)
		s += '</div></font></td> '
		s += '</tr> '

		s += '<tr> '
		s += '<td width="50%" style="border: solid 1 #000000" nowrap=""><font size="2" face="微软雅黑">'
		s += '<div>'
		s += '<span style="font-size: 14px; white-space: normal; background-color: transparent; line-height: 1.5;"></span>'
		s += '<span style="font-size: 14px; line-height: 21px; white-space: normal; background-color: transparent;">%s</span>' % self.__summary_subtitle_result_unactive
		s += '</div></font></td> '
		s += '<td width="50%" style="border: solid 1 #000000" nowrap=""><font size="2" face="微软雅黑">'
		s += '<div>'
		s += '{0}'.format(unactive)
		s += '</div></font></td> '
		s += '</tr> '

		s += '<tr> '
		s += '<td width="50%" style="border: solid 1 #000000" nowrap=""><font size="2" face="微软雅黑">'
		s += '<div>'
		s += '<span style="background-color: transparent; line-height: 1.5;">%s</span>'% self.__summary_subtitle_result_total
		s += '</div></font></td> '
		s += '<td width="50%" style="border: solid 1 #000000" nowrap=""><font size="2" face="微软雅黑">'
		s += '<div>'
		s += '{0}'.format(total)
		s += '</div></font></td>'
		s += '</tr>'

		s += '</tbody>'
		s += '</table>'
		s += '</div>'
		s += '<div>'
		s += '<br />'
		s += '</div>'
		s += '<hr id="FMSigSeperator" style="width: 210px; height: 1px;" color="#b5c4df" size="1" align="left" /> '
		s += '<div>'
		s += '<span id="_FoxFROMNAME">'
		s += '<div style="MARGIN: 10px; FONT-FAMILY: verdana; FONT-SIZE: 10pt">'
		s += '<div>'
		s += '<div>'
		s += '%s' % self.__summary_subtitle_signature
		s += '</div>'
		s += '</div>'
		s += '<div>'
		s += '<br />'
		s += '</div>'
		s += '</div></span>'
		s += '</div> '
		s += '<div id="divFMReplyBody"></div>'
		s += '</div> </td> '
		s += '</tr> '
		s += '</tbody>'
		s += '</table>'
		s += '</body>'
		s += '</html>'

		att = MIMEText(s, 'html', 'utf-8')
		msg.attach(att)

		#构造附件
		att = MIMEText(open(f, 'rb').read(), 'base64', 'gb2312')
		att["Content-Type"] = 'application/octet-stream'
		att["Content-Disposition"] = 'attachment; filename="%s"' % file_name
		msg.attach(att)

		#加邮件头
		msg['from'] = sender
		msg['subject'] = Header('%s-%s(%s)' % (self.__summary_title, self.name(), self.start_time()),'UTF-8')
		msg['to'] = ";".join(delivers.values())
		#发送邮件
		try:
			server = smtplib.SMTP_SSL(smtp, 465)
			server.login(user, password)
			server.sendmail(msg['from'], delivers.values(), msg.as_string())
			server.quit()
			if not silence:
				p.stop(color_str("OK", "green") + " %s " % (self.__language == "Chinese" and "投递给" or "delivers:") + str(["%s<%s>" % (name, email) for name, email in delivers.items()]))
		except smtplib.SMTPRecipientsRefused:
			print(color_str('Recipient refused', "red"))
		except smtplib.SMTPAuthenticationError as err:
			s = ""
			for x in err:
				if type(x) == type(''):
					s += x.decode('gb2312') + " "
				else:
					s += str(x) + " "
			else:
				if not silence:
					p.stop(color_str(s, "red"))
				else:
					print(color_str(s, "red"))
		except smtplib.SMTPSenderRefused:
			print(color_str('Sender refused', "red"))
		except smtplib.SMTPException as e:
		    print (color_str(e.message, "red"))

			



		
