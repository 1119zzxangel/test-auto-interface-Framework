import os                                  # 导入操作系统模块
import xlrd                                # 导入xls读取库
from conf import setting                   # 导入项目配置
from xlutils.copy import copy              # 导入excel复制修改工具
from common.recordlog import logs          # 导入日志模块
import xlwt                                # 导入excel写入库

class OperationExcel(object):              # excel操作封装类
    """封装读取/写入Excel文件的数据"""

    def __init__(self, filename=None):     # 初始化方法
        try:                                # 异常捕获
            if filename is not None:        # 判断是否传入文件路径
                self.__filename = filename  # 使用传入的文件名
            else:                           # 未传入则使用配置文件路径
                self.__filename = setting.FILE_PATH['EXCEL']
            self.__sheet_id = setting.SHEET_ID  # 获取配置中的sheet索引
        except Exception as e:              # 捕获异常
            logs.error(e)                  # 打印错误日志
        self.__GLOBAL_TABLE = self.xls_obj()  # 获取excel对象
        self.colx = 0                      # 默认列索引为0

    def xls_obj(self):                     # 创建excel对象方法
        xls_obj = ''                       # 定义空对象
        # 判断文件后缀是否为.xlsx
        if os.path.splitext(self.__filename)[-1] != '.xlsx':
            # 打开excel文件，保留格式
            data = xlrd.open_workbook(self.__filename, formatting_info=True)
            xls_obj = data.sheets()[self.__sheet_id]  # 获取指定sheet
        else:
            # 错误日志，只支持.xls格式
            logs.error('Excel文件的格式必须为.xls格式，请重新另存为xls格式！')
            exit()                         # 退出程序
        return xls_obj                     # 返回sheet对象

    def get_rows(self):                    # 获取总行数
        """获取xls文件总行数"""
        return self.__GLOBAL_TABLE.nrows   # 返回总行数

    def get_cols(self):                    # 获取总列数
        """获取总列数"""
        return self.__GLOBAL_TABLE.ncols   # 返回总列数

    def get_cell_value(self, row, col):    # 获取单元格数据
        """获取单元格的值"""
        return self.__GLOBAL_TABLE.cell_value(row, col)  # 返回单元格值

    def settingStyle(self):                # 设置单元格样式
        """设置样式,该功能暂时未生效"""
        style = xlwt.easyfont("font:bold 1,color red")  # 粗体红色字体

    def write_xls_value(self, row, col, value):  # 写入单元格数据
        """写入数据"""
        try:                                  # 异常捕获
            # 打开原文件
            init_table = xlrd.open_workbook(self.__filename, formatting_info=True)
            copy_table = copy(init_table)     # 复制工作簿
            sheet = copy_table.get_sheet(self.__filename)  # 获取sheet
            sheet.write(row, col, value)      # 写入数据
            copy_table.save(self.__filename)  # 保存文件
        except PermissionError:               # 文件被占用异常
            logs.error("请先关闭xls文件")     # 打印日志
            exit()                            # 退出

    def get_each_line(self, row):            # 获取整行数据
        """获取每一行数据"""
        try:                                 # 异常捕获
            return self.__GLOBAL_TABLE.row_values(row)  # 返回整行数据
        except Exception as exp:             # 捕获异常
            logs.error(exp)                  # 打印错误日志

    def get_each_column(self, col=None):     # 获取整列数据
        """获取每一列数据"""
        if col is None:                      # 未传参则使用默认列
            return self.__GLOBAL_TABLE.col_values(self.colx)
        else:                                # 使用传入的列索引
            return self.__GLOBAL_TABLE.col_values(col)