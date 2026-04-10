import sys  # 导入系统模块，用于系统相关操作
from conf import setting  # 导入项目全局配置文件
import logging  # 导入Python内置日志模块，用于日志记录
import os  # 导入操作系统模块，用于文件、目录操作
import time  # 导入时间模块，用于生成日志文件名
from logging.handlers import RotatingFileHandler  # 按文件大小滚动备份日志
import datetime  # 导入日期模块，用于计算过期日志

# 从配置文件中读取日志存放目录路径
log_path = setting.FILE_PATH["LOG"]
# 判断日志目录是否存在
if not os.path.exists(log_path):
    # 不存在则创建日志目录
    os.mkdir(log_path)
# 拼接日志文件完整路径，按日期生成日志文件名
logfile_name = log_path + r"\test.{}.logs".format(time.strftime("%Y%m%d"))


class RecordLog:
    """日志模块：负责日志输出、文件存储、过期清理"""

    def __init__(self):
        # 初始化时自动执行过期日志清理
        self.handle_overdue_log()

    def handle_overdue_log(self):
        """处理过期日志文件，自动清理30天前的日志"""
        # 获取系统当前时间
        now_time = datetime.datetime.now()
        # 定义时间偏移量：往前推30天
        offset_date = datetime.timedelta(days=-30)
        # 计算30天前的时间戳
        before_date = (now_time + offset_date).timestamp()
        # 获取日志目录下所有文件
        files = os.listdir(log_path)
        # 遍历所有日志文件
        for file in files:
            # 判断是否为文件（有后缀名）
            if os.path.splitext(file)[1]:
                # 拼接文件完整路径
                filepath = log_path + "\\" + file
                # 获取文件创建时间戳
                file_create_time = os.path.getctime(filepath)
                # 如果文件创建时间早于30天前，则删除
                if file_create_time < before_date:
                    os.remove(filepath)
                else:
                    # 否则跳过
                    continue

    def output_logging(self):
        """获取并配置logger对象，输出日志到文件和控制台"""
        # 获取日志器对象
        logger = logging.getLogger(__name__)
        # 防止重复添加handler导致日志重复打印
        if not logger.handlers:
            # 设置全局日志级别
            logger.setLevel(setting.LOG_LEVEL)
            # 设置日志输出格式：级别、时间、文件名、行号、模块、方法、消息
            log_format = logging.Formatter(
                '%(levelname)s - %(asctime)s - %(filename)s:%(lineno)d -[%(module)s:%(funcName)s] - %(message)s')
            # 创建按文件大小滚动的文件处理器
            fh = RotatingFileHandler(filename=logfile_name, mode='a', maxBytes=5242880,
                                     backupCount=7, encoding='utf-8')
            # 设置文件日志级别
            fh.setLevel(setting.LOG_LEVEL)
            # 设置文件日志格式
            fh.setFormatter(log_format)
            # 将文件处理器添加到日志器
            logger.addHandler(fh)

            # 创建控制台输出处理器
            sh = logging.StreamHandler()
            # 设置控制台日志级别
            sh.setLevel(setting.STREAM_LOG_LEVEL)
            # 设置控制台日志格式
            sh.setFormatter(log_format)
            # 将控制台处理器添加到日志器
            logger.addHandler(sh)
        # 返回配置好的日志器
        return logger


# 实例化日志类
apilog = RecordLog()
# 获取全局可用的日志对象
logs = apilog.output_logging()