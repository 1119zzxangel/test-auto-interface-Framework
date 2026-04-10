import xml.etree.ElementTree as et                               # 导入Python内置XML解析库
from conf.setting import FILE_PATH                               # 导入配置文件中的路径配置
from common.recordlog import logs                                # 导入日志工具

class OperXML:                                                   # 定义XML操作类

    def read_xml(self, filename, tags, attr_value):              # 读取XML指定标签文本
        """读取XML文件标签值"""
        root = ''                                                # 初始化根节点变量
        file_path = {                                            # 拼接XML文件路径
            'file': FILE_PATH['XML'] + '\\' + filename
        }
        try:                                                     # 捕获解析异常
            tree = et.parse(file_path['file'])                   # 解析XML文件生成树结构
            root = tree.getroot()                                # 获取XML根节点
        except Exception as e:
            logs.error(e)                                        # 打印异常日志

        child_text = ''                                           # 初始化存储文本的变量
        for child in root.iter(tags):                            # 遍历所有指定标签
            att = child.attrib                                   # 获取当前标签的所有属性
            if ''.join(list(att.values())) == attr_value:        # 判断属性值是否匹配
                child_text = child.text.strip()                  # 匹配则获取文本并去空格
            if child:                                            # 如果当前标签有子节点
                for i in child:                                  # 遍历子节点
                    attr = i.attrib                              # 获取子节点属性
                    if ''.join(list(attr.values())) == attr_value:  # 判断子节点属性是否匹配
                        child_text = i.text.strip()               # 获取子节点文本

        return child_text                                        # 返回最终读取到的文本

    def get_attribute_value(self, filename, tags):               # 获取标签的属性字典
        """读取标签属性值"""
        root = ''                                                # 初始化根节点
        file_path = {'file': FILE_PATH['RESULTXML'] + '\\' + filename}  # 拼接结果XML路径
        try:
            tree = et.parse(file_path['file'])                   # 解析XML文件
            root = tree.getroot()                                # 获取根节点
        except Exception as e:
            logs.error(e)                                        # 异常日志

        attr = [child.attrib for child in root.iter(tags)][0]    # 获取第一个匹配标签的属性字典

        return attr                                              # 返回属性字典