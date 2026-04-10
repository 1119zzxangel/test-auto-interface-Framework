import pandas as pd  # 导入pandas数据处理库，用于读取CSV文件
from common.recordlog import logs  # 导入日志模块，记录日志信息
import traceback  # 导入异常追踪模块，捕获详细报错信息

def read_csv(filepath, col_name):  # 定义读取CSV文件的函数
    """
    :param filepath: csv目录
    :param col_name: 取值的列名
    usecols：需要读取的列，可以是列的位置编号，也可以是列的名称
    error_bad_lines = False  当某行数据有问题时，不报错，直接跳过，处理脏数据时使用
    :return:
    """
    try:  # 尝试执行读取逻辑，捕获可能出现的异常
        df = pd.read_csv(filepath, encoding="GBK")  # 使用pandas读取CSV文件，指定编码为GBK，生成DataFrame对象
        data = df[col_name].tolist()  # 根据传入的列名获取对应列数据，并转换为Python列表
        return data  # 返回读取到的列数据列表
    except Exception:  # 捕获所有类型的异常
        logs.error(str(traceback.format_exc()))  # 捕获详细异常堆栈信息，并以error级别写入日志