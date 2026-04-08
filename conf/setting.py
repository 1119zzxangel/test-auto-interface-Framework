import logging
import os
import sys
# 动态获取项目根目录，绝对不写死路径，保证项目在不同环境、不同目录下都能正常运行
DIR_BASE = os.path.dirname(os.path.dirname(__file__))
sys.path.append(DIR_BASE)
# sys.path：Python 解释器的模块搜索路径列表，Python 只会从这个列表里的目录找要导入的模块
# append(DIR_BASE)：把项目根目录添加到 Python 的搜索路径中
# 作用：让项目内所有模块都能被正确导入，彻底解决ModuleNotFoundError
# log日志输出级别
LOG_LEVEL = logging.DEBUG  # 文件
STREAM_LOG_LEVEL = logging.DEBUG  # 控制台

# 接口超时时间，单位/s
API_TIMEOUT = 60

# excel文件的sheet页，默认读取第一个sheet页的数据，int类型，第一个sheet为0，以此类推0.....9
SHEET_ID = 0

# 生成的测试报告类型，可以生成两个风格的报告，allure或tm
REPORT_TYPE = 'allure'

# 是否发送钉钉消息
dd_msg = False

# 文件路径,通过 os.path.join 动态拼接项目根目录 DIR_BASE，生成所有关键文件 / 目录的绝对路径
FILE_PATH = {
    'CONFIG': os.path.join(DIR_BASE, 'conf/config.ini'),
    'LOG': os.path.join(DIR_BASE, 'logs'),
    'YAML': os.path.join(DIR_BASE),
    'TEMP': os.path.join(DIR_BASE, 'report/temp'),
    'TMR': os.path.join(DIR_BASE, 'report/tmreport'),
    'EXTRACT': os.path.join(DIR_BASE, 'extract.yaml'),
    'XML': os.path.join(DIR_BASE, 'data/sql'),
    'RESULTXML': os.path.join(DIR_BASE, 'report'),
    'EXCEL': os.path.join(DIR_BASE, 'data', '测试数据.xls')
}

# 默认请求头信息,定义接口请求的默认全局请求头，所有接口请求默认携带该头信息
LOGIN_HEADER = {
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive'
}

# 路径基准：DIR_BASE 定义项目根目录，所有路径基于此动态生成
# 配置读取：operationConfig.py 读取 FILE_PATH['CONFIG'] 路径下的 config.ini
# 全局调用：框架中所有需要路径 / 请求头 / 开关的模块（接口请求、日志、报告、通知），都直接导入 setting.py 中的常量
# 运行规则：pytest 运行时，优先读取 setting.py 中的路径与默认配置，再结合 config.ini 环境参数执行
