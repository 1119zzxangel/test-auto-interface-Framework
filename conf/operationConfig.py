import sys  # 导入系统相关模块，用于获取异常信息
import traceback  # 导入异常追踪模块，用于打印详细的错误堆栈信息

# sys.path.insert(0, "..")  # 将上级目录添加到Python搜索路径（注释状态，未启用）

import configparser  # 导入Python内置的ini配置文件解析模块
from conf import setting  # 从conf包导入项目配置文件setting.py
from common.recordlog import logs  # 从公共模块导入日志对象，用于记录日志

class OperationConfig:
    """封装读取*.ini配置文件模块"""  # 类的文档字符串，说明该类作用

    def __init__(self, filepath=None):  # 构造方法，初始化时执行，filepath为配置文件路径（可选参数）
        # 判断是否传入文件路径，未传入则使用默认配置路径
        if filepath is None:
            # 私有属性，存储配置文件路径（从setting配置中读取CONFIG路径）
            self.__filepath = setting.FILE_PATH['CONFIG']
        else:
            # 传入了路径则使用传入的路径
            self.__filepath = filepath

        # 创建ConfigParser对象，用于解析ini文件
        self.conf = configparser.ConfigParser()
        try:
            # 读取指定路径的ini配置文件，指定编码为utf-8防止中文乱码
            self.conf.read(self.__filepath, encoding='utf-8')
        except Exception as e:
            # 捕获读取文件时的异常，获取异常类型、值、追踪对象
            exc_type, exc_value, exc_obj = sys.exc_info()
            # 记录异常堆栈信息到错误日志
            logs.error(str(traceback.print_exc(exc_obj)))

        # 初始化报告类型，从配置文件读取REPORT_TYPE下的type值
        self.type = self.get_report_type('type')

    def get_item_value(self, section_name):
        """
        :param section_name: 根据ini文件的头部值获取全部值
        :return:以字典形式返回
        """
        # 获取指定section下所有的键值对
        items = self.conf.items(section_name)
        # 将键值对转换为字典并返回
        return dict(items)

    def get_section_for_data(self, section, option):
        """
        :param section: ini文件头部值
        :param option:头部值下面的选项
        :return:
        """
        try:
            # 获取指定section下指定option的值
            values = self.conf.get(section, option)
            # 返回获取到的值
            return values
        except Exception as e:
            # 捕获取值异常，记录详细错误堆栈
            logs.error(str(traceback.format_exc()))
            # 异常时返回空字符串，避免程序中断
            return ''

    def write_config_data(self, section, option_key, option_value):
        """
        写入数据到ini配置文件中
        :param section: 头部值
        :param option_key: 选项值key
        :param option_value: 选项值value
        :return:
        """
        # 判断要写入的section是否不存在
        if section not in self.conf.sections():
            # 添加一个新的section
            self.conf.add_section(section)
            # 在该section下设置键值对
            self.conf.set(section, option_key, option_value)
        else:
            # section已存在，记录信息日志，提示写入失败
            logs.info('"%s"值已存在，写入失败' % section)
        # 以写入模式打开配置文件
        with open(self.__filepath, 'w', encoding='utf-8') as f:
            # 将修改后的配置写入文件
            self.conf.write(f)

    def get_section_mysql(self, option):
        # 封装获取MYSQL配置的方法
        return self.get_section_for_data("MYSQL", option)

    def get_section_redis(self, option):
        # 封装获取REDIS配置的方法
        return self.get_section_for_data("REDIS", option)

    def get_section_clickhouse(self, option):
        # 封装获取CLICKHOUSE配置的方法
        return self.get_section_for_data("CLICKHOUSE", option)

    def get_section_mongodb(self, option):
        # 封装获取MONGODB配置的方法
        return self.get_section_for_data("MongoDB", option)

    def get_report_type(self, option):
        # 封装获取报告类型配置的方法
        return self.get_section_for_data('REPORT_TYPE', option)

    def get_section_ssh(self, option):
        # 封装获取SSH配置的方法
        return self.get_section_for_data("SSH", option)

    def get_section_jenkins(self, option):
        # 封装获取JENKINS配置的方法
        return self.get_section_for_data("JENKINS", option)