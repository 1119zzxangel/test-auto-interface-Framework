import re  # 导入正则模块，用于提取测试报告链接
import jenkins  # 导入jenkins库，用于操作Jenkins接口
from conf.operationConfig import OperationConfig  # 导入配置读取类，获取Jenkins配置信息

class PJenkins(object):  # Jenkins操作封装类
    conf = OperationConfig()  # 初始化配置对象

    def __init__(self):  # 构造方法，初始化Jenkins连接
        # 定义私有配置字典，从配置文件读取Jenkins连接信息
        self.__config = {
            'url': self.conf.get_section_jenkins('url'),  # Jenkins地址
            'username': self.conf.get_section_jenkins('username'),  # Jenkins用户名
            'password': self.conf.get_section_jenkins('password'),  # Jenkins密码/token
            'timeout': int(self.conf.get_section_jenkins('timeout'))  # 连接超时时间
        }
        self.__server = jenkins.Jenkins(**self.__config)  # 创建Jenkins连接对象
        self.job_name = self.conf.get_section_jenkins('job_name')  # 获取要操作的任务名称

    def get_job_number(self):  # 获取最近一次构建号
        """读取jenkins job构建号"""
        build_number = self.__server.get_job_info(self.job_name).get('lastBuild').get('number')
        return build_number  # 返回最新构建号

    def get_build_job_status(self):  # 获取最近一次构建结果状态
        """读取构建完成的状态"""
        build_num = self.get_job_number()  # 获取最新构建号
        job_status = self.__server.get_build_info(self.job_name, build_num).get('result')  # 获取构建结果
        return job_status  # 返回SUCCESS/FAILURE/ABORTED

    def get_console_log(self):  # 获取控制台输出日志
        """获取控制台日志"""
        console_log = self.__server.get_build_console_output(self.job_name, self.get_job_number())
        return console_log  # 返回完整控制台日志

    def get_job_description(self):  # 获取任务描述信息
        """返回job描述信息"""
        description = self.__server.get_job_info(self.job_name).get('description')  # 任务描述
        url = self.__server.get_job_info(self.job_name).get('url')  # 任务URL
        return description, url  # 返回描述和地址

    def get_build_report(self):  # 获取Jenkins内置测试报告
        """返回第n次构建的测试报告"""
        report = self.__server.get_build_test_report(self.job_name, self.get_job_number())
        return report  # 返回测试报告数据

    def report_success_or_fail(self):  # 统计并格式化测试结果
        """统计测试报告用例成功数、失败数、跳过数以及成功率、失败率"""
        report_info = self.get_build_report()  # 获取测试报告
        pass_count = report_info.get('passCount')  # 通过用例数
        fail_count = report_info.get('failCount')  # 失败用例数
        skip_count = report_info.get('skipCount')  # 跳过用例数
        total_count = int(pass_count) + int(fail_count) + int(skip_count)  # 总用例数
        duration = int(report_info.get('duration'))  # 执行时长（秒）
        hour = duration // 3600  # 计算小时
        minute = duration % 3600 // 60  # 计算分钟
        seconds = duration % 3600 % 60  # 计算秒
        execute_duration = f'{hour}时{minute}分{seconds}秒'  # 格式化时长
        # 拼接结果文本
        content = f'本次测试共执行{total_count}个测试用例，成功：{pass_count}个; 失败：{fail_count}个; 跳过：{skip_count}个; 执行时长：{hour}时{minute}分{seconds}秒'
        # 从控制台日志中用正则提取allure报告链接
        console_log = self.get_console_log()
        report_line = re.search(r'http://192.168.105.36:8088/job/hbjjapi/(.*?)allure', console_log).group(0)
        # 组装返回的报告信息
        report_info = {
            'total': total_count,
            'pass_count': pass_count,
            'fail_count': fail_count,
            'skip_count': skip_count,
            'execute_duration': execute_duration,
            'report_line': report_line
        }
        return report_info  # 返回格式化后的报告

if __name__ == '__main__':  # 主程序测试入口
    p = PJenkins()  # 创建对象
    res = p.report_success_or_fail()  # 获取测试报告
    print(res)  # 打印结果