import base64  # 导入base64加密模块
import calendar  # 导入日历模块，用于获取月份天数
import datetime  # 导入日期时间处理模块
import hashlib  # 导入MD5/SHA等加密模块
import os.path  # 导入路径处理模块
import random  # 导入随机数模块
import re  # 导入正则表达式模块
import time  # 导入时间模块
from hashlib import sha1  # 导入SHA1加密方法
from conf.setting import DIR_BASE  # 导入项目根路径配置
from pandas.tseries.offsets import Day  # 导入日期偏移量工具
from common.operationcsv import read_csv  # 导入CSV读取工具
from common.readyaml import ReadYamlData  # 导入YAML读取工具
import csv  # 导入CSV文件操作模块

class DebugTalk:  # 工具类，提供各类通用辅助方法

    def __init__(self):  # 构造方法
        self.read = ReadYamlData()  # 初始化YAML读取对象

    def get_extract_data(self, node_name, randoms=None) -> str:  # 从extract.yaml获取数据，支持随机/索引/全部读取
        """
        获取extract.yaml数据，首先判断randoms是否为数字类型，如果不是就获取下一个node节点的数据
        :param node_name: extract.yaml文件中的key值
        :param randoms: int类型，0：随机读取；-1：读取全部，返回字符串；-2：返回列表；其他按索引取值
        :return:
        """
        data = self.read.get_extract_yaml(node_name)  # 读取指定节点数据
        if randoms is not None and bool(re.compile(r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$').match(randoms)):  # 判断是否为数字
            randoms = int(randoms)  # 转为int
            data_value = {
                randoms: self.get_extract_order_data(data, randoms),  # 按索引取第N个
                0: random.choice(data),         # 0 = 随机取一个
                -1: ','.join(data),            # -1 = 全部拼成字符串
                -2: ','.join(data).split(','), # -2 = 返回列表
            }
            data = data_value[randoms]  # 根据参数取值
        else:
            data = self.read.get_extract_yaml(node_name, randoms)  # 直接读取
        return data  # 返回结果

    def get_extract_order_data(self, data, randoms):  # 按索引顺序取值
        """获取extract.yaml数据，不为0、-1、-2，则按顺序读取文件key的数据"""
        if randoms not in [0, -1, -2]:
            return data[randoms - 1]  # 返回索引对应数据

    def md5_encryption(self, params):  # MD5加密
        """参数MD5加密"""
        enc_data = hashlib.md5()  # 创建MD5对象
        enc_data.update(params.encode("utf-8"))  # 传入待加密字符串
        return enc_data.hexdigest()  # 返回加密结果

    def sha1_encryption(self, params):  # SHA1加密
        """参数sha1加密"""
        enc_data = sha1()  # 创建SHA1对象
        enc_data.update(params.encode("utf-8"))  # 更新内容
        return enc_data.hexdigest()  # 返回摘要

    def base64_encryption(self, params):  # Base64加密
        """base64加密"""
        base_params = params.encode("utf-8")  # 字符串转bytes
        encr = base64.b64encode(base_params)  # 加密
        return encr  # 返回密文

    def timestamp(self):  # 获取10位时间戳
        """获取当前时间戳，10位"""
        t = int(time.time())
        return t

    def timestamp_thirteen(self):  # 获取13位时间戳
        """获取当前的时间戳，13位"""
        t = int(time.time()) * 1000
        return t

    def start_time(self):  # 获取前一天时间
        """获取当前时间的前一天标准时间"""
        now_time = datetime.datetime.now()
        day_before_time = (now_time - 1 * Day()).strftime("%Y-%m-%d %H:%M:%S")
        return day_before_time

    def end_time(self):  # 获取当前时间
        """获取当前时间标准时间格式"""
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return now_time

    def start_forward_time(self):  # 前15天日期
        """获取当前时间的前15天标准时间，年月日"""
        now_time = datetime.datetime.now()
        day_before_time = (now_time - 15 * Day()).strftime("%Y-%m-%d")
        return day_before_time

    def start_after_time(self):  # 后7天日期
        """获取当前时间的后7天标准时间，年月日"""
        now_time = datetime.datetime.now()
        day_after_time = (now_time + 7 * Day()).strftime("%Y-%m-%d")
        return day_after_time

    def end_year_time(self):  # 当前年月日
        """获取当前时间标准时间格式，年月日"""
        now_time = datetime.datetime.now().strftime("%Y-%m-%d")
        return now_time

    def today_zero_tenstamp(self):  # 今日0点10位时间戳
        """获取当天00:00:00时间戳，10位时间戳"""
        time_stamp = int(time.mktime(datetime.date.today().timetuple()))
        return time_stamp

    def today_zero_stamp(self):  # 今日0点13位时间戳
        """获取当天00:00:00时间戳，13位时间戳"""
        time_stamp = int(time.mktime(datetime.date.today().timetuple())) * 1000
        return time_stamp

    def specified_zero_tamp(self, days):  # 指定日期0点时间戳
        """获取当前日期指定日期的00:00:00时间戳，days：往前为负数，往后为整数"""
        tom = datetime.date.today() + datetime.timedelta(days=int(days))
        date_tamp = int(time.mktime(time.strptime(str(tom), '%Y-%m-%d'))) * 1000
        return date_tamp

    def specified_end_tamp(self, days):  # 指定日期23:59:59时间戳
        """获取当前日期指定日期的23:59:59时间戳，days：往前为负数，往后为整数"""
        tom = datetime.date.today() + datetime.timedelta(days=int(days) + 1)
        date_tamp = int(time.mktime(time.strptime(str(tom), '%Y-%m-%d'))) - 1
        return date_tamp * 1000

    def today_end_stamp(self):  # 今日23:59:59时间戳
        """获取当天23:59:59时间戳"""
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        today_end_time = int(time.mktime(time.strptime(str(tomorrow), '%Y-%m-%d'))) - 1
        return today_end_time * 1000

    def month_start_time(self):  # 本月第一天
        """获取本月第一天标准时间，年月日"""
        now = datetime.datetime.now()
        this_month_start = datetime.datetime(now.year, now.month, 1).strftime("%Y-%m-%d")
        return this_month_start

    def month_end_time(self):  # 本月最后一天
        """获取本月最后一天标准时间，年月日"""
        now = datetime.datetime.now()
        this_month_end = datetime.datetime(now.year, now.month, calendar.monthrange(now.year, now.month)[1]).strftime("%Y-%m-%d")
        return this_month_end

    def month_first_time(self):  # 本月1号0点时间戳
        """本月1号00:00:00时间戳，13位"""
        now = datetime.datetime.now()
        this_month_start = datetime.datetime(now.year, now.month, 1)
        first_time_stamp = int(time.mktime(this_month_start.timetuple())) * 1000
        return first_time_stamp

    def fenceAlarm_alarmType_random(self):  # 随机报警类型
        alarm_type = ["1", "3", "8", "2", "5", "6"]
        fence_alarm = random.choice(alarm_type)
        return fence_alarm

    def fatigueAlarm_alarmType_random(self):  # 疲劳报警随机类型
        alarm_type = ["1", "3", "8"]
        fatigue_alarm = random.choice(alarm_type)
        return fatigue_alarm

    def jurisdictionAlarm_random(self):  # 权限报警随机类型
        alarm_type = ["1", "3", "8", "2", "5", "6", "9"]
        jurisdiction_alarm = random.choice(alarm_type)
        return jurisdiction_alarm

    def vehicle_random(self):  # 从CSV随机取车牌号
        """从csv中随机读取车牌号"""
        data = read_csv(os.path.join(DIR_BASE, 'data', 'vehicleNo.csv'), 'vno')
        vel_num = random.choice(data)
        return vel_num

    def read_csv_data(self, file_name, index):  # 读取CSV里的用户名、密码
        """读取csv数据，csv文件中不用带字段名，直接写测试数据即可"""
        with open(os.path.join(DIR_BASE, 'data', file_name), 'r', encoding='utf-8') as f:
            csv_reader = list(csv.reader(f))
            user_lst, passwd_lst = [], []
            for user, passwd in csv_reader:
                user_lst.append(user)
                passwd_lst.append(passwd)
            return user_lst[0], passwd_lst[0]

    def get_baseurl(self, host):  # 从配置读取接口环境URL
        from conf.operationConfig import OperationConfig
        conf = OperationConfig()
        url = conf.get_section_for_data('api_envi', host)
        return url