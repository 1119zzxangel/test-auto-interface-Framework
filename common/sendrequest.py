import json  # 处理JSON格式数据，用于参数序列化和解析
import allure  # 测试报告框架，用于日志、附件、步骤展示
import pytest  # 测试框架，用于断言、用例标记、失败标记
import requests  # 发送HTTP/HTTPS接口请求的核心库
import urllib3  # 处理HTTPS请求警告，关闭证书验证提示
import time  # 时间控制，可用于请求间隔等待

from conf import setting  # 导入项目全局配置文件
from common.recordlog import logs  # 导入统一日志记录工具
from requests import utils  # requests工具类，处理cookie转换
from common.readyaml import ReadYamlData  # 导入YAML读写工具，用于存储cookie
from urllib3.exceptions import InsecureRequestWarning  # 忽略HTTPS证书警告


class SendRequest:
    """统一发送接口请求封装类，目前支持GET、POST及通用请求方法"""

    def __init__(self, cookie=None):
        """
        初始化请求对象
        :param cookie: 可选，传入全局cookie
        """
        self.cookie = cookie  # 存储cookie，供请求使用
        self.read = ReadYamlData()  # 实例化YAML工具类，用于写入cookie

    def get(self, url, data, header):
        """
        封装GET请求方法（旧版单独请求，已逐步被send_request替代）
        :param url: 接口地址
        :param data: 请求参数
        :param header: 请求头
        :return: 封装后的响应字典
        """
        # 关闭SSL证书不安全警告
        requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            # 判断参数是否为空，发送不同请求
            if data is None:
                response = requests.get(url, headers=header, cookies=self.cookie, verify=False)
            else:
                response = requests.get(url, data, headers=header, cookies=self.cookie, verify=False)
        # 捕获requests库所有请求异常
        except requests.RequestException as e:
            logs.error(e)
            return None
        # 捕获其他未知异常
        except Exception as e:
            logs.error(e)
            return None

        # 计算接口响应时间（毫秒）
        res_ms = response.elapsed.microseconds / 1000
        # 计算接口响应时间（秒）
        res_second = response.elapsed.total_seconds()

        # 定义统一返回的响应字典
        response_dict = dict()
        response_dict['code'] = response.status_code  # 状态码
        response_dict['text'] = response.text  # 响应文本
        # 尝试解析JSON中的body字段
        try:
            response_dict['body'] = response.json().get('body')
        except Exception:
            response_dict['body'] = ''
        response_dict['res_ms'] = res_ms
        response_dict['res_second'] = res_second
        return response_dict

    def post(self, url, data, header):
        """
        封装POST请求方法（旧版单独请求，已逐步被send_request替代）
        :param url: 接口地址
        :param data: 请求参数
        :param header: 请求头
        :return: 封装后的响应字典
        """
        # 关闭SSL证书不安全警告
        requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            # 判断参数是否为空，发送不同请求
            if data is None:
                response = requests.post(url, header, cookies=self.cookie, verify=False)
            else:
                response = requests.post(url, data, headers=header, cookies=self.cookie, verify=False)
        # 捕获请求异常
        except requests.RequestException as e:
            logs.error(e)
            return None
        except Exception as e:
            logs.error(e)
            return None

        # 计算响应时间
        res_ms = response.elapsed.microseconds / 1000
        res_second = response.elapsed.total_seconds()

        # 封装统一响应格式
        response_dict = dict()
        response_dict['code'] = response.status_code
        response_dict['text'] = response.text
        # 尝试解析JSON中的body
        try:
            response_dict['body'] = response.json().get('body')
        except Exception:
            response_dict['body'] = ''
        response_dict['res_ms'] = res_ms
        response_dict['res_second'] = res_second
        return response_dict

    def send_request(self, **kwargs):
        """
        核心请求发送方法：基于session会话发送所有类型请求
        支持GET/POST/PUT/DELETE等所有请求方式
        :param kwargs: 动态请求参数（url、method、headers、data、json等）
        :return: 原始响应对象
        """
        session = requests.session()  # 创建requests会话，保持cookie/登录态
        result = None  # 初始化响应结果
        cookie = {}  # 存储提取的cookie

        try:
            # 发送请求（支持所有method）
            result = session.request(**kwargs)
            # 从响应中提取cookie并转为字典格式
            set_cookie = requests.utils.dict_from_cookiejar(result.cookies)
            # 如果有cookie，则写入yaml文件，供后续接口使用
            if set_cookie:
                cookie['Cookie'] = set_cookie
                self.read.write_yaml_data(cookie)
                logs.info("cookie：%s" % cookie)

            # 打印接口返回信息
            logs.info("接口返回信息：%s" % result.text if result.text else result)

        # 捕获连接异常（网络不通、地址错误）
        except requests.exceptions.ConnectionError:
            logs.error("ConnectionError--连接异常")
            pytest.fail("接口请求异常，可能是request的连接数过多或请求速度过快导致程序报错！")
        # 捕获HTTP协议异常
        except requests.exceptions.HTTPError:
            logs.error("HTTPError--http异常")
        # 捕获所有请求相关异常
        except requests.exceptions.RequestException as e:
            logs.error(e)
            pytest.fail("请求异常，请检查系统或数据是否正常！")

        return result  # 返回原始响应对象

    def run_main(self, name, url, case_name, header, method, cookies=None, file=None, **kwargs):
        """
        对外统一调用入口：日志打印 + Allure报告 + 发送请求
        是测试用例直接调用的核心方法
        :param name: 接口名称
        :param url: 请求地址
        :param case_name: 用例名称
        :param header: 请求头
        :param method: 请求方法（GET/POST/PUT等）
        :param cookies: cookie
        :param file: 上传文件
        :param kwargs: 其他请求参数（data/json/params等）
        :return: 接口响应对象
        """
        try:
            # 控制台打印请求信息日志
            logs.info('接口名称：%s' % name)
            logs.info('请求地址：%s' % url)
            logs.info('请求方式：%s' % method)
            logs.info('测试用例名称：%s' % case_name)
            logs.info('请求头：%s' % header)
            logs.info('Cookie：%s' % cookies)

            # 将请求参数转为JSON字符串
            req_params = json.dumps(kwargs, ensure_ascii=False)
            # 判断参数类型，将请求参数附加到Allure报告
            if "data" in kwargs.keys():
                allure.attach(req_params, '请求参数', allure.attachment_type.TEXT)
                logs.info("请求参数：%s" % kwargs)
            elif "json" in kwargs.keys():
                allure.attach(req_params, '请求参数', allure.attachment_type.TEXT)
                logs.info("请求参数：%s" % kwargs)
            elif "params" in kwargs.keys():
                allure.attach(req_params, '请求参数', allure.attachment_type.TEXT)
                logs.info("请求参数：%s" % kwargs)
        except Exception as e:
            logs.error(e)

        # 关闭HTTPS警告
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # 调用核心send_request发送请求
        response = self.send_request(
            method=method,
            url=url,
            headers=header,
            cookies=cookies,
            files=file,
            timeout=setting.API_TIMEOUT,
            verify=False,
            **kwargs
        )
        return response
