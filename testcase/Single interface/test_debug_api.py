import allure  ## 导入allure-pytest插件，用于生成美观的测试报告
import pytest   ## 导入pytest插件，用于测试框架

from common.readyaml import get_testcase_yaml  ## 导入yaml数据驱动插件，用于读取yaml文件
from base.apiutil import RequestBase  ## 导入请求工具类，用于发送http请求
from base.generateId import m_id, c_id  ## 导入生成id的工具类，用于生成模块id和用例id

# allure.feature：给测试类打模块标签，在Allure报告中显示一级菜单
@allure.feature(next(m_id) + '用户管理模块（单接口）')  ## 定义测试模块，用于组织测试用例
class TestUserManager:
    """
    用户管理模块测试类
    包含：新增、修改、删除、查询 4个单接口测试用例
    """
    # 场景，allure报告的目录结构
    # allure.story：对应allure报告中的二级子模块
    @allure.story(next(c_id) + "新增用户")
    # 测试用例执行顺序设置
    # pytest.mark.run(order=1)：设置用例执行顺序为第1个
    @pytest.mark.run(order=1)
    # 参数化，yaml数据驱动
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/Single interface/addUser.yaml"))
    def test_add_user(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])     ## 设置测试用例的标题，用于在报告中显示
        RequestBase().specification_yaml(base_info, testcase)  ## 调用请求工具类，发送http请求  

    @allure.story(next(c_id) + "修改用户")
    @pytest.mark.run(order=2)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/Single interface/updateUser.yaml"))
    def test_update_user(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + "删除用户")
    @pytest.mark.run(order=3)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/Single interface/deleteUser.yaml"))
    def test_delete_user(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + "查询用户")
    @pytest.mark.run(order=4)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/Single interface/queryUser.yaml"))
    def test_query_user(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)
