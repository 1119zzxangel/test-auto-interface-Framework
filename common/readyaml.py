import yaml  # 导入yaml模块，用于解析和写入YAML格式测试数据文件
import traceback  # 导入异常追踪模块，用于打印详细的错误堆栈信息
import os  # 导入操作系统模块，用于文件路径、目录、文件存在性判断

from common.recordlog import logs  # 从公共模块导入日志对象，统一记录日志
from conf.operationConfig import OperationConfig  # 导入配置操作类，读取ini配置
from conf.setting import FILE_PATH  # 导入项目路径配置，获取文件存储路径

# 读取【测试用例 YAML】，专门给 pytest 做数据驱动，要跑用例 → 用 get_testcase_yaml
def get_testcase_yaml(file):
    """
    读取外部YAML测试用例文件，封装成pytest数据驱动格式
    :param file: YAML文件路径
    :return: 返回格式化后的用例列表
    """
    testcase_list = []  # 初始化空列表，存储处理后的测试用例数据
    try:
        # 以只读、UTF-8编码打开YAML测试用例文件
        with open(file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)  # 安全加载YAML文件内容，转为Python对象

            # 判断YAML数据长度是否<=1（标准结构：baseInfo + testCase）
            if len(data) <= 1:
                yam_data = data[0]  # 取第一个元素（包含baseInfo和testCase）
                base_info = yam_data.get('baseInfo')  # 提取公共基础信息（模块、地址等）

                # 遍历测试用例列表
                for ts in yam_data.get('testCase'):
                    param = [base_info, ts]  # 组合成 [基础信息, 单条用例]
                    testcase_list.append(param)  # 添加到最终用例列表
                return testcase_list  # 返回处理好的用例数据
            else:
                return data  # 非标准结构，直接返回原始数据
    # 捕获编码异常
    except UnicodeDecodeError:
        logs.error(f"[{file}]文件编码格式错误，--尝试使用utf-8编码解码YAML文件时发生了错误，请确保你的yaml文件是UTF-8格式！")
    # 捕获文件不存在异常
    except FileNotFoundError:
        logs.error(f'[{file}]文件未找到，请检查路径是否正确')
    # 捕获其他未知异常
    except Exception as e:
        logs.error(f'获取【{file}】文件数据时出现未知错误: {str(e)}')

# 通用 YAML 读写工具类，负责【参数关联、提取变量、配置读取】，要存 token、取变量、写文件 → 用 ReadYamlData
class ReadYamlData:
    """读写接口的YAML格式测试数据，主要用于用例读取、参数关联、token/变量存储"""

    def __init__(self, yaml_file=None):
        """
        初始化方法，传入YAML文件路径
        :param yaml_file: YAML文件路径（可选）
        """
        if yaml_file is not None:
            self.yaml_file = yaml_file  # 若传入文件，则赋值给对象属性
        else:
            pass  # 未传入则不处理

        self.conf = OperationConfig()  # 实例化配置读取对象
        self.yaml_data = None  # 初始化YAML数据变量

    @property
    def get_yaml_data(self):
        """
        装饰器方法：获取测试用例yaml数据
        :return: 返回list/dict格式的YAML数据
        """
        # Loader=yaml.FullLoader表示加载完整的YAML语言，避免任意代码执行，无此参数控制台报Warning
        try:
            # 打开YAML文件并读取
            with open(self.yaml_file, 'r', encoding='utf-8') as f:
                self.yaml_data = yaml.safe_load(f)  # 安全加载数据
                return self.yaml_data  # 返回读取结果
        except Exception:
            logs.error(str(traceback.format_exc()))  # 异常时打印堆栈并记录日志

    def write_yaml_data(self, value):
        """
        写入数据到extract.yaml，主要用于接口关联（token、订单号、用户ID等）
        写入数据需为dict，allow_unicode=True表示支持中文，sort_keys=False保持原始顺序
        :param value: 写入数据，必须为字典
        :return:
        """
        file = None  # 初始化文件句柄
        file_path = FILE_PATH['EXTRACT']  # 获取参数提取文件路径

        # 自动创建文件所在目录，不存在则创建，存在不报错
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            # 以追加模式打开文件，写入参数
            file = open(file_path, 'a', encoding='utf-8')

            # 判断传入数据是否为字典格式
            if isinstance(value, dict):
                # 将字典转为YAML格式，支持中文、不排序
                write_data = yaml.dump(value, allow_unicode=True, sort_keys=False)
                file.write(write_data)  # 写入文件
            else:
                logs.info('写入[extract.yaml]的数据必须为dict格式')  # 格式错误提示
        except Exception:
            logs.error(str(traceback.format_exc()))  # 异常日志
        finally:
            if file:
                file.close()  # 确保文件关闭

    def clear_yaml_data(self):
        """
        清空extract.yaml文件数据（每次执行用例前清空，避免数据污染）
        :return:
        """
        with open(FILE_PATH['EXTRACT'], 'w') as f:
            f.truncate()  # 清空文件内容

    def get_extract_yaml(self, node_name, second_node_name=None):
        """
        读取extract.yaml中提取的全局变量（token、id等）
        :param node_name: 一级key
        :param second_node_name: 二级key（可选）
        :return: 读取到的变量值
        """
        # 判断文件是否存在
        if os.path.exists(FILE_PATH['EXTRACT']):
            pass
        else:
            logs.error('extract.yaml不存在')
            file = open(FILE_PATH['EXTRACT'], 'w')  # 不存在则创建
            file.close()
            logs.info('extract.yaml创建成功！')

        try:
            # 读取extract.yaml内容
            with open(FILE_PATH['EXTRACT'], 'r', encoding='utf-8') as rf:
                ext_data = yaml.safe_load(rf)

                # 没有传二级节点，直接取一级节点
                if second_node_name is None:
                    return ext_data[node_name]
                # 传了二级节点，取嵌套值
                else:
                    return ext_data[node_name][second_node_name]
        except Exception as e:
            logs.error(f"【extract.yaml】没有找到：{node_name},--%s" % e)

    def get_testCase_baseInfo(self, case_info):
        """
        获取testcase yaml文件的baseInfo公共数据（模块名、地址、标题等）
        :param case_info: yaml数据，dict类型
        :return:
        """
        pass

    def get_method(self):
        """
        获取YAML测试用例中的请求方法（GET/POST/PUT/DELETE）
        :return: 请求方法字符串
        """
        yal_data = self.get_yaml_data()
        metd = yal_data[0].get('method')
        return metd

    def get_request_parame(self):
        """
        获取yaml测试数据中的请求参数，去掉baseInfo，只返回用例数据
        :return: 接口请求参数列表
        """
        data_list = []  # 初始化参数列表
        yaml_data = self.get_yaml_data()  # 读取YAML数据
        del yaml_data[0]  # 删除第一条baseInfo基础数据

        # 遍历剩余所有测试用例
        for da in yaml_data:
            data_list.append(da)
        return data_list  # 返回纯参数列表