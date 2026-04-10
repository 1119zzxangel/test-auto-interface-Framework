import smtplib                                 # 导入邮件发送模块
from email.mime.text import MIMEText           # 导入邮件文本内容构造类
from conf.operationConfig import OperationConfig  # 导入配置读取类
from email.mime.multipart import MIMEMultipart  # 导入多部件邮件构造类
from email.mime.application import MIMEApplication  # 导入附件处理类
from conf import setting                       # 导入配置文件
from common.recordlog import logs              # 导入日志模块
import re                                      # 导入正则表达式模块

conf = OperationConfig()                       # 创建配置实例对象

class SendEmail(object):
    """构建邮件主题、正文、附件"""

    def __init__(
            self,
            host=conf.get_section_for_data('EMAIL', 'host'),  # 读取邮箱SMTP地址
            user=conf.get_section_for_data('EMAIL', 'user'),  # 读取发件人邮箱
            passwd=conf.get_section_for_data('EMAIL', 'passwd')):  # 读取授权码
        self.__host = host                                  # 私有变量：SMTP服务器
        self.__user = user                                  # 私有变量：发件人账号
        self.__passwd = passwd                              # 私有变量：授权码

    def build_content(self, subject, email_content, addressee=None, atta_file=None):
        """
        构建邮件格式，邮件正文、附件
        @param subject: 邮件主题
        @param addressee: 收件人，在配置文件中以;分割
        @param email_content: 邮件正文内容
        @return:
        """
        user = 'liaison officer' + '<' + self.__user + '>'  # 构造发件人显示名称
        if addressee is None:                               # 判断是否传入收件人
            addressee = conf.get_section_for_data('EMAIL', 'addressee').split(';')  # 读取配置收件人
        else:
            addressee = addressee.split(';')                # 按;分割收件人
        message = MIMEMultipart()                           # 创建多部件邮件对象
        message['Subject'] = subject                        # 设置邮件主题
        message['From'] = user                              # 设置发件人
        message['To'] = ';'.join([re.search(r'(.*)(@)', emi).group(1) + "<" + emi + ">" for emi in addressee])  # 格式化收件人

        text = MIMEText(email_content, _subtype='plain', _charset='utf-8')  # 构造纯文本正文
        message.attach(text)                                      # 添加正文到邮件

        if atta_file is not None:                                 # 判断是否有附件
            atta = MIMEApplication(open(atta_file, 'rb').read())  # 读取附件内容
            atta['Content-Type'] = 'application/octet-stream'    # 设置附件类型
            atta['Content-Disposition'] = 'attachment; filename="testresult.xls"'  # 设置附件名称
            message.attach(atta)                                  # 添加附件

        try:
            service = smtplib.SMTP_SSL(self.__host)              # 创建SSL连接
            service.login(self.__user, self.__passwd)            # 登录邮箱
            service.sendmail(user, addressee, message.as_string())  # 发送邮件
        except smtplib.SMTPConnectError as e:
            logs.error('邮箱服务器连接失败！', e)                # 捕获连接异常
        except smtplib.SMTPAuthenticationError as e:
            logs.error('邮箱服务器认证错误,POP3/SMTP服务未开启,密码应填写授权码!', e)  # 认证失败
        except smtplib.SMTPSenderRefused as e:
            logs.error('发件人地址未经验证！', e)                # 发件人异常
        except smtplib.SMTPDataError as e:
            logs.error('发送的邮件内容包含了未被许可的信息，或被系统识别为垃圾邮件！', e)  # 内容异常
        except Exception as e:
            logs.error(e)                                        # 其他异常
        else:
            logs.info('邮件发送成功!')                           # 发送成功日志
            service.quit()                                       # 关闭连接

class BuildEmail(SendEmail):
    """发送邮件"""

    def main(self, success, failed, error, not_running, atta_file=None, *args):
        """
        :param success: list类型
        :param failed: list类型
        :param error: list类型
        :param not_running: list类型
        :param atta_file: 附件路径
        :param args:
        :return:
        """
        success_num = len(success)                               # 成功用例数
        fail_num = len(failed)                                   # 失败用例数
        error_num = len(error)                                   # 错误用例数
        notrun_num = len(not_running)                           # 未运行用例数
        total = success_num + fail_num + error_num + notrun_num  # 总用例数
        execute_case = success_num + fail_num                   # 已执行用例数
        pass_result = "%.2f%%" % (success_num / execute_case * 100)  # 通过率
        fail_result = "%.2f%%" % (fail_num / execute_case * 100)    # 失败率
        err_result = "%.2f%%" % (error_num / execute_case * 100)    # 错误率
        subject = conf.get_section_for_data('EMAIL', 'subject')  # 读取邮件主题
        addressee = conf.get_section_for_data('EMAIL', 'addressee').split(';')  # 读取收件人
        content = "     ***项目接口测试，共测试接口%s个，通过%s个，失败%s个，错误%s个，未执行%s个，通过率%s，失败率%s，错误率%s。详细测试结果请参见附件。" % (total, success_num, fail_num, error_num, notrun_num, pass_result, fail_result, err_result)  # 邮件正文
        self.build_content(addressee, subject, content, atta_file)  # 调用发送方法