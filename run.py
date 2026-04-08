import shutil        # 文件复制、移动
import pytest        # 测试用例运行框架
import os            # 系统命令、路径操作
import webbrowser    # 自动打开浏览器
from conf.setting import REPORT_TYPE  # 从配置文件读取报告类型

if __name__ == '__main__':

    if REPORT_TYPE == 'allure':
        pytest.main([
        '-s', '-v',            # 输出详细日志
        '--alluredir=./report/temp',  # 把测试结果存到 temp 目录
        './testcase',          # 运行 testcase 下所有用例
        '--clean-alluredir',   # 运行前清空旧报告
        '--junitxml=./report/results.xml'  # 生成JUnit格式结果
    ])

        shutil.copy('./environment.xml', './report/temp') # 复制环境配置文件到报告目录（展示环境信息用）
        os.system('allure serve ./report/temp')

    elif REPORT_TYPE == 'tm':
        pytest.main(['-vs', '--pytest-tmreport-name=testReport.html', '--pytest-tmreport-path=./report/tmreport'])
        webbrowser.open_new_tab(os.getcwd() + '/report/tmreport/testReport.html')
