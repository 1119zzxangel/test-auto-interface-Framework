# -*- coding: utf-8 -*-
import time
import pytest  # 测试框架
from common.readyaml import ReadYamlData  # 读yaml数据
from base.removefile import remove_file  # 删文件
from common.dingRobot import send_dd_msg  # 发钉钉消息
from conf.setting import dd_msg  # 钉钉开关（True/False）
import warnings  # 忽略告警

yfd = ReadYamlData()
# 定义一个会话级别的fixture，整个测试过程只执行一次，自动运行
# 全局前置钩子（测试前自动执行）
@pytest.fixture(scope="session", autouse=True)
def clear_extract():
    # 禁用HTTPS告警，ResourceWarning
    warnings.simplefilter('ignore', ResourceWarning)

    yfd.clear_yaml_data()  # 清空yaml数据
    # 清空测试报告目录下的所有文件
    remove_file("./report/temp", ['json', 'txt', 'attach', 'properties'])


def generate_test_summary(terminalreporter):
    """生成测试结果摘要字符串"""
    total = terminalreporter._numcollected
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    error = len(terminalreporter.stats.get('error', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    duration = time.time() - terminalreporter._sessionstarttime

    summary = f"""
    自动化测试结果，通知如下，请着重关注测试失败的接口，具体执行结果如下：
    测试用例总数：{total}
    测试通过数：{passed}
    测试失败数：{failed}
    错误数量：{error}
    跳过执行数量：{skipped}
    执行总时长：{duration}
    """
    print(summary)
    return summary


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """pytest钩子函数：测试全部结束后自动执行"""
    """自动收集pytest框架执行的测试结果并打印摘要信息"""
    summary = generate_test_summary(terminalreporter)
    if dd_msg:
        send_dd_msg(summary)## 如果配置里开了钉钉通知，就发消息
# 测试前自动清环境，测试后自动统计结果，开启开关就自动发钉钉通知。

# 存放全项目通用的全局 fixture / 钩子，例如：
# 1. 全局环境清理、日志初始化
# 2. 钉钉 / 邮件通知钩子
# 3. 全局配置加载、敏感信息处理
# 4. 全项目通用的前后置