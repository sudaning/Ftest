#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

# 号码相关
# 号段解析，号码类型解析
# 号码RN生成
#

from neko import color_str, MySQL
import os,sys

class Number:
	def __init__(self, mysql_exe_fun, number):
		self.execute = mysql_exe_fun
		self.number = number

	def __del__(self):
		pass

	@property
	def section(self):
		prev_exe_number = ""
		this_exe_number = ""
		for digit in [11, 7, 6, 5, 4, 3]:
			this_exe_number = self.number[:digit]
			if prev_exe_number == this_exe_number:
				continue
			else:
				prev_exe_number = this_exe_number
			
			for data in self.execute(
				"SELECT a.telno, a.areacode, a.operator, b.pcode, a.ccode, a.international " + 
				"FROM tb_telno_info a " + 
				"LEFT JOIN tb_areacode_pcode b ON a.areacode = b.areacode " + 
				"WHERE a.telno = '%s'" % this_exe_number):
				if data:
					return {"telno":data[0], "areacode":data[1], "operator":data[2], 
						"provcode":data[3], "citycode":data[4], "international":data[5], "test_num":this_exe_number}
		else:
			return {}

	@property
	def type(self):
		l = len(self.number)
		if l >= 1 and self.number[0] == '0':# /* 固定号码(带区号) */
			return "telephone"
		elif l == 11 and self.number[0] == '1':# /* 手机号码 */
			return "mobilephone"
		elif l >= 3 and self.number[:3] == "400":# /* 400XXX号码 */
			return "400"
		elif l >= 2 and self.number[:2] == "95":# /* 95XXX号码 */
			return "95"
		else:# /* 无法判断号码类型 */
			return ""

class Rn:

	__cmcc = "00" #/* 中国移动 */
	__cu = "01" #/* 中国联通 */
	__ct = "02" #/* 中国电信 */

	def __init__(self, host, port, user, password, dbname, debug=False):
		self.mysql = MySQL(host, port, user, password, dbname)
		self.debug = debug

	def __del__(self):
		self.mysql = None

	# 匹配度计算
	def __num_match_degree(self, test_num, tar_num):
		# 没有配置匹配规则，则认为是任意匹配
		test_num = test_num.strip()
		tar_num = tar_num.strip()
		if not len(tar_num):
			return 0

		pos = test_num.find(tar_num)
		if -1 == pos:
			return -1 # 完全不匹配
		elif 0 == pos:
			return len(tar_num)
		else:
			return -1 # 不满足从头匹配规则

	# 特例表指定RN
	def __rn_particular(self, caller, callee):
		
		rn = ""
		cur_caller_match_degree = -1
		for data in self.mysql.execute("SELECT xh_telno,dest_telno,rn FROM tb_appoint_link"):
			match_degree = self.__num_match_degree(caller, data[0])
			if -1 == match_degree:
				continue
			elif match_degree >= cur_caller_match_degree:
				cur_caller_match_degree = match_degree;
				match_degree = self.__num_match_degree(callee, data[1]);
				if -1 == match_degree:
					cur_caller_match_degree = -1
					continue
				else:
					rn = data[2]
		else:
			return rn

	# APPID和业务指定RN
	def __rn_appid_bussiness(self, bus_code, appid):

		rn_app = ""

		for data in self.mysql.execute("SELECT appid,route_code FROM tb_app_info WHERE route_code <> ''"):
			if data[0] == appid:
				rn_app = data[1]
				break

		if not rn_app:
			for data in self.mysql.execute("SELECT bus_type,status FROM tb_code_type"):
				if data[0] == bus_code and data[1] == "01":
					rn_app = "0000"
					break

		if rn_app:
			return "A" + bus_code + rn_app
		else:
			return ""

	def __rn_realm1(self, caller_num_type, callee_num_type):
			return caller_num_type == "95" and "4" or \
				caller_num_type == "telephone" and "2" or \
				caller_num_type == "400" and "5" or \
				caller_num_type == "mobilephone" and \
					(callee_num_type == "mobilephone" and "3" or "1") or \
				""
	
	def __rn_realm_rule1(self, status, operators, number):
		#/* 若数据库中没有获得运营商码，域2也按照查不到信息处理 */
		realm2 = (None == status or len(operators) == 0) and self.__cmcc or self.operators
		realm3 = "{:0>5}".format(number)[:5]
		return realm2, realm3

	def __rn_realm_rule2(self, status, number_type, operators, area_prov_code):
		if self.debug:
			print(status != None, number_type, operators, area_prov_code)
		realm2_4 = ""
		realm3_5 = ""
		__realm2_4 = number_type == "telephone" and self.__ct or self.__cmcc
		if status == None:
			realm2_4 = __realm2_4
			realm3_5 = "00000"
		else:
			realm2_4 = len(operators) != 0 and operators or __realm2_4
			realm3_5 = "{0:0<5}".format(area_prov_code)[:5]
		return realm2_4, realm3_5


	# 主被叫归属地生成RN码
	def __rn_normal(self, caller, callee):
		# 主叫域
		num = Number(self.mysql.execute, caller)
		caller_num_type = num.type
		caller_num_section = num.section or {}

		# 被叫域
		num = Number(self.mysql.execute, callee)
		callee_num_type = num.type
		callee_num_section = num.section or {}

		realm1 = self.__rn_realm1(caller_num_type, callee_num_type)
		realm2, realm3 = "", ""
		realm4, realm5 = "", ""

		if self.debug:
			print(caller_num_type, caller_num_section, callee_num_type, callee_num_section)

		if caller_num_type in ["telephone", "mobilephone"]:
			if caller_num_type == "mobilephone" and callee_num_type == "mobilephone":
				realm2, realm3 = self.__rn_realm_rule2(None, caller_num_type, \
					caller_num_section.get("operator", ""), caller_num_section.get("provcode", ""))
			else:
				realm2, realm3 = self.__rn_realm_rule2(caller_num_section, caller_num_type, \
					caller_num_section.get("operator", ""), caller_num_section.get("provcode", ""))
		
			realm4, realm5 = self.__rn_realm_rule2(callee_num_section, callee_num_type, \
				callee_num_section.get("operator", ""), callee_num_section.get("provcode", ""))
		elif caller_num_type in ["95"]:
			realm2, realm3 = self.__rn_realm_rule1(caller_num_section, \
				caller_num_section.get("operator", ""), caller)
			realm4, realm5 = self.__rn_realm_rule2(callee_num_section, callee_num_type, \
				caller_num_section.get("operator", ""), caller_num_section.get("areacode", ""))
		elif caller_num_type in ["400"]:
			realm2, realm3 = self.__rn_realm_rule1(caller_num_section, \
				caller_num_section.get("operator", ""), "00000")
			realm4, realm5 = self.__rn_realm_rule2(callee_num_section, callee_num_type, \
				caller_num_section.get("operator", ""), caller_num_section.get("areacode", ""))
		else:
			realm2, realm3 = self.__rn_realm_rule1(caller_num_section, self.__cmcc, "00000")
			realm4, realm5 = self.__rn_realm_rule2(callee_num_section, callee_num_type, \
				caller_num_section.get("operator", ""), caller_num_section.get("areacode", ""))
		if self.debug:
			print(realm1, realm2, realm3, realm4, realm5)
		return realm1 + realm2 + realm3 + realm4 + realm5

	# 正常生成RN码
	def __normal(self, bus_code, appid, caller, callee):
		rn = self.__rn_particular(caller, callee)
		if self.debug:
			print(rn)
		if not rn:
			rn = self.__rn_appid_bussiness(bus_code, appid) + self.__rn_normal(caller, callee)
		if self.debug:
			print(rn)
		return rn

	# 指定RN码
	def __specify(self, bus_code, appid, trunkid):
		pass

	def get(self, bus_code, appid, caller, callee, mode = "normal", trunkid = ""):
		if self.debug:
			print(bus_code, appid, caller, callee, mode, trunkid)
		if mode in ["normal"]:
			return self.__normal(bus_code, appid, caller, callee)
		elif mode in ["specify"]:
			return self.__specify(bus_code, appid, trunkid)
		else:
			return ""

if __name__ == '__main__':
	from optparse import OptionParser 
	parser = OptionParser()
	parser.add_option('-s', '--host', dest='host', default='10.0.33.54', help='MySQL server IP address')
	parser.add_option('-p', '--port', dest='port', type="int", default=3306, help='MySQL server port')
	parser.add_option('-u', '--user', dest='user', default='root', help='MySQL server user')
	parser.add_option('-a', '--password', dest='password', default='33E9.com', help='MySQL server password')
	parser.add_option('-d', '--dbname', dest='dbname', default='e9cloud_home', help='MySQL server dbname')

	parser.add_option('--bus_type', dest='bus_type', default='05', help='business type')
	parser.add_option('--appid', dest='appid', default='382212dc3e9011e69698a1f6651c9441', help='appid')
	parser.add_option('--caller', dest='caller', default='075566603330', help='caller number')
	parser.add_option('--callee', dest='callee', default='95311', help='callee number')

	(options, args) = parser.parse_args()
	
	rn = Rn(options.host, options.port, options.user, options.password, options.dbname, debug=True)
	print(rn.get(options.bus_type, options.appid, options.caller, options.callee))
	
	

	
