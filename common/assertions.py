import traceback                                    # 导入异常追踪模块
import allure                                       # 导入Allure测试报告模块
import jsonpath                                     # 导入JSON路径提取工具
import operator                                     # 导入比较运算符工具

from common.recordlog import logs                   # 导入日志工具
from common.connection import ConnectMysql          # 导入MySQL数据库连接类

class Assertions:                                   # 接口断言工具类
    """"
    接口断言模式，支持
    1）响应文本字符串包含模式断言
    2）响应结果相等断言
    3）响应结果不相等断言
    4）响应结果任意值断言
    5）数据库断言
    """
# 遍历预期断言字段，通过 jsonpath 递归提取接口响应中任意层级的字段值，判断预期值是否被包含在实际结果中，失败则计数并记录报告与日志。
    def contains_assert(self, value, response, status_code):  # 字符串包含断言，全层级查找，包含即可
        """
        字符串包含断言模式，断言预期结果的字符串是否包含在接口的响应信息中
        :param value: 预期结果，yaml文件的预期结果值
        :param response: 接口实际响应结果
        :param status_code: 响应状态码
        :return: 返回结果的状态标识
        """
        flag = 0                                     # 断言状态标识，0成功，其他失败
        for assert_key, assert_value in value.items():  # 遍历预期断言键值对
            if assert_key == "status_code":          # 判断是否断言状态码
                if assert_value != status_code:      # 状态码不相等
                    flag += 1                       # 失败标记+1
                    allure.attach(f"预期结果：{assert_value}\n实际结果：{status_code}", '响应代码断言结果:失败',
                                  attachment_type=allure.attachment_type.TEXT)  # 报告记录失败
                    logs.error("contains断言失败：接口返回码【%s】不等于【%s】" % (status_code, assert_value))  # 日志记录
            else:
                resp_list = jsonpath.jsonpath(response, "$..%s" % assert_key)  # jsonpath提取实际值
                if isinstance(resp_list[0], str):   # 判断提取结果是否为字符串，jsonpath 返回的是列表，转成字符串方便判断 xxx in yyy
                    resp_list = ''.join(resp_list)   # 拼接成字符串
                if resp_list:                        # 判断提取结果存在
                    assert_value = None if assert_value.upper() == 'NONE' else assert_value  # 处理None值，预期写 NONE 就转成 Python 的 None
                    if assert_value in resp_list:    # 预期值包含在实际结果中
                        logs.info("字符串包含断言成功：预期结果【%s】,实际结果【%s】" % (assert_value, resp_list))
                    else:
                        flag = flag + 1              # 断言失败，标记+1
                        allure.attach(f"预期结果：{assert_value}\n实际结果：{resp_list}", '响应文本断言结果：失败',
                                      attachment_type=allure.attachment_type.TEXT)  # 报告记录
                        logs.error("响应文本断言失败：预期结果为【%s】,实际结果为【%s】" % (assert_value, resp_list))
        return flag                                  # 返回断言标记
# 校验预期与实际结果均为字典，提取共同 key 构建对比字典，判断两者是否完全相等，记录结果并返回失败标记。
    def equal_assert(self, expected_results, actual_results, statuc_code=None):  # 相等断言
        """
        相等断言模式
        :param expected_results: 预期结果，yaml文件validation值
        :param actual_results: 接口实际响应结果
        :return:
        """
        flag = 0                                     # 初始化失败标记
        if isinstance(actual_results, dict) and isinstance(expected_results, dict):  # 判断是否都是字典
            common_keys = list(expected_results.keys() & actual_results.keys())[0]  # 获取共同key
            new_actual_results = {common_keys: actual_results[common_keys]}  # 生成新实际结果字典
            eq_assert = operator.eq(new_actual_results, expected_results)  # 比较两个字典是否相等
            if eq_assert:                             # 断言成功
                logs.info(f"相等断言成功：接口实际结果：{new_actual_results}，等于预期结果：" + str(expected_results))
                allure.attach(f"预期结果：{str(expected_results)}\n实际结果：{new_actual_results}", '相等断言结果：成功',
                              attachment_type=allure.attachment_type.TEXT)
            else:
                flag += 1                            # 失败标记+1
                logs.error(f"相等断言失败：接口实际结果{new_actual_results}，不等于预期结果：" + str(expected_results))
                allure.attach(f"预期结果：{str(expected_results)}\n实际结果：{new_actual_results}", '相等断言结果：失败',
                              attachment_type=allure.attachment_type.TEXT)
        else:
            raise TypeError('相等断言--类型错误，预期结果和接口实际响应结果必须为字典类型！')  # 类型错误抛出异常
        return flag                                   # 返回标记
# 校验预期与实际结果均为字典，提取共同 key 构建对比字典，判断两者是否不相等，记录结果并返回失败标记。
    def not_equal_assert(self, expected_results, actual_results, statuc_code=None):  # 不相等断言
        """
        不相等断言模式
        :param expected_results: 预期结果，yaml文件validation值
        :param actual_results: 接口实际响应结果
        :return:
        """
        flag = 0                                     # 初始化失败标记
        if isinstance(actual_results, dict) and isinstance(expected_results, dict):  # 判断类型
            common_keys = list(expected_results.keys() & actual_results.keys())[0]  # 获取共同key
            new_actual_results = {common_keys: actual_results[common_keys]}  # 生成新实际结果
            eq_assert = operator.ne(new_actual_results, expected_results)  # 判断不相等
            if eq_assert:                             # 不相等则成功
                logs.info(f"不相等断言成功：接口实际结果：{new_actual_results}，不等于预期结果：" + str(expected_results))
                allure.attach(f"预期结果：{str(expected_results)}\n实际结果：{new_actual_results}", '不相等断言结果：成功',
                              attachment_type=allure.attachment_type.TEXT)
            else:
                flag += 1                            # 相等则失败
                logs.error(f"不相等断言失败：接口实际结果{new_actual_results}，等于预期结果：" + str(expected_results))
                allure.attach(f"预期结果：{str(expected_results)}\n实际结果：{new_actual_results}", '不相等断言结果：失败',
                              attachment_type=allure.attachment_type.TEXT)
        else:
            raise TypeError('不相等断言--类型错误，预期结果和接口实际响应结果必须为字典类型！')
        return flag                                   # 返回标记
# 获取预期字段的 key，从接口响应最外层读取对应 value，与预期值精确比对是否相等，捕获异常并返回断言标记。
    def assert_response_any(self, actual_results, expected_results):  # 任意响应字段断言
        """
        断言接口响应信息中的body的任何属性值
        :param actual_results: 接口实际响应信息
        :param expected_results: 预期结果，在接口返回值的任意值
        :return: 返回标识,0表示测试通过，非0则测试失败
        """
        flag = 0                                     # 初始化失败标记
        try:                                         # 异常捕获
            exp_key = list(expected_results.keys())[0]  # 获取预期key
            if exp_key in actual_results:            # 判断key存在
                act_value = actual_results[exp_key]  # 获取实际值
                rv_assert = operator.eq(act_value, list(expected_results.values())[0])  # 比较值
                if rv_assert:                         # 相等成功
                    logs.info("响应结果任意值断言成功")
                else:
                    flag += 1                        # 不相等失败
                    logs.error("响应结果任意值断言失败")
        except Exception as e:
            logs.error(e)                            # 记录异常
            raise                                    # 抛出异常
        return flag                                   # 返回标记

    def assert_response_time(self, res_time, exp_time):  # 响应时间断言
        """
        通过断言接口的响应时间与期望时间对比,接口响应时间小于预期时间则为通过
        :param res_time: 接口的响应时间
        :param exp_time: 预期的响应时间
        :return:
        """
        try:
            assert res_time < exp_time               # 断言响应时间小于预期
            return True                              # 成功返回True
        except Exception as e:
            logs.error('接口响应时间[%ss]大于预期时间[%ss]' % (res_time, exp_time))  # 记录超时
            raise                                    # 抛出异常

    def assert_mysql_data(self, expected_results):   # 数据库断言
        """
        数据库断言
        :param expected_results: 预期结果，yaml文件的SQL语句
        :return: 返回flag标识，0表示正常，非0表示测试不通过
        """
        flag = 0                                     # 初始化失败标记
        conn = ConnectMysql()                        # 创建数据库连接
        db_value = conn.query_all(expected_results)  # 执行SQL查询
        if db_value is not None:                     # 查询到数据则成功
            logs.info("数据库断言成功")
        else:
            flag += 1                                # 未查询到则失败
            logs.error("数据库断言失败，请检查数据库是否存在该数据！")
        return flag                                   # 返回标记

    def assert_result(self, expected, response, status_code):  # 断言总入口
        """
        断言，通过断言all_flag标记，all_flag==0表示测试通过，否则为失败
        :param expected: 预期结果
        :param response: 实际响应结果
        :param status_code: 响应code码
        :return:
        """
        all_flag = 0                                 # 总失败标记
        try:                                         # 异常捕获
            logs.info("yaml文件预期结果：%s" % expected)  # 打印预期结果
            for yq in expected:                      # 遍历预期断言列表
                for key, value in yq.items():         # 遍历每种断言类型
                    if key == "contains":             # 包含断言
                        flag = self.contains_assert(value, response, status_code)
                        all_flag = all_flag + flag
                    elif key == "eq":                 # 相等断言
                        flag = self.equal_assert(value, response)
                        all_flag = all_flag + flag
                    elif key == 'ne':                 # 不相等断言
                        flag = self.not_equal_assert(value, response)
                        all_flag = all_flag + flag
                    elif key == 'rv':                 # 任意字段断言
                        flag = self.assert_response_any(actual_results=response, expected_results=value)
                        all_flag = all_flag + flag
                    elif key == 'db':                 # 数据库断言
                        flag = self.assert_mysql_data(value)
                        all_flag = all_flag + flag
                    else:
                        logs.error("不支持此种断言方式")

        except Exception as exceptions:
            logs.error('接口断言异常，请检查yaml预期结果值是否正确填写!')
            raise exceptions                         # 抛出异常

        if all_flag == 0:                            # 无失败标记则用例通过
            logs.info("测试成功")
            assert True
        else:
            logs.error("测试失败")
            assert False