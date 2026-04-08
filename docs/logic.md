## 1. 项目概述

**功能说明**：本项目是一个基于 pytest 框架的接口自动化测试项目，主要用于测试各种 HTTP 接口的功能和性能。项目采用数据驱动的方式，使用 YAML 文件存储测试用例，支持参数化测试、接口关联、断言验证、报告生成等功能。

**核心模块**：

- `run.py`：项目入口文件，负责启动测试并生成报告
- `conftest.py`：pytest 配置文件，定义全局 fixture 和钩子函数
- `base/apiutil.py`：核心接口测试类，负责处理接口请求和响应
- `common/sendrequest.py`：请求发送模块，负责发送 HTTP 请求
- `common/readyaml.py`：YAML 解析模块，负责读取和解析测试用例
- `common/assertions.py`：断言模块，负责验证接口响应

## 2. 项目运行路径

**功能说明**：项目运行路径模块详细描述了测试项目的完整运行路径，从用户执行 run.py 开始，到生成报告并在浏览器中打开结束。这个路径帮助测试人员和开发人员更好地理解测试项目的运行流程。

**完整运行路径**：

### 1. 程序入口启动

**动作**：用户执行 `python run.py`。

**细节**：

- `run.py` 调用 `pytest.main()` 启动测试会话
- **文件路径**：`Test-Automation-Framework-main/run.py`
- **功能说明**：run.py 是整个测试框架的入口文件，负责启动 pytest 测试运行器并生成测试报告。它会根据配置的报告类型（Allure 或 TM）来执行相应的测试命令，并在测试完成后自动打开测试报告。
- **核心代码**：

```plain
if __name__ == '__main__':
    if REPORT_TYPE == 'allure':
        pytest.main([
        '-s', '-v',            # 输出详细日志
        '--alluredir=./report/temp',  # 把测试结果存到 temp 目录
        './testcase',          # 运行 testcase 下所有用例
        '--clean-alluredir',   # 运行前清空旧报告
        '--junitxml=./report/results.xml'  # 生成JUnit格式结果
    ])

        shutil.copy('./environment.xml', './report/temp') # 复制环境配置文件到报告目录
        os.system('allure serve ./report/temp')
```

**代码来源**：`Test-Automation-Framework-main/run.py`
**功能说明**：run.py 是整个测试框架的入口文件，负责启动 pytest 测试运行器并生成测试报告。它会根据配置的报告类型（Allure 或 TM）来执行相应的测试命令，并在测试完成后自动打开测试报告。

- **命令行参数解析**：

- - `-s`：关闭输出捕获，允许在控制台直接显示 `print` 或日志输出，方便调试和查看实时输出
  - `-v`：增加测试输出的详细程度，显示每个测试用例的名称及其执行状态
  - `--alluredir=./report/temp`：指定 Allure 报告中间数据的输出目录，pytest 会在此生成 JSON/XML 等原始数据
  - `./testcase`：指定测试用例所在的目录路径，pytest 会在此目录下递归查找并执行测试文件
  - `--clean-alluredir`：运行前清空旧报告数据，避免数据残留影响报告的准确性
  - `--junitxml=./report/results.xml`：生成 JUnit 格式的测试结果，方便与 Jenkins 等 CI 工具集成

### 2. 框架初始化与配置加载

**动作**：`pytest` 启动，加载全局配置。（pytest 框架初始化时，加载的是**pytest 框架级配置**）

**细节**：

- 调用 `_prepareconfig`：函数入口，启动配置加载流程；
- 解析 `pytest.ini`/`pyproject.toml`：内部调用配置文件解析逻辑，按优先级读取框架运行规则；
- 解析命令行传入的自定义参数：内部调用命令行解析逻辑，参数优先级最高，覆盖配置文件；
- 自动导入根目录及子目录的 `conftest.py`：内部调用 `_set_initial_conftests`方法，扫描并加载所有 `conftest.py；`
- 加载内置及第三方插件（如 allure-pytest）：函数初始化阶段就完成插件加载，为后续配置解析提供支持；
- 最终整合生成全局 `config`对象：函数的最终输出，整合所有配置，贯穿整个测试会话
- 而`conf/setting.py`这类业务配置，不属于框架初始化加载范围，需要在测试代码中手动读取，用于业务参数管理。

**conftest.py 的作用**：

- **全局前置钩子**：conftest.py 是 pytest 的配置文件，在项目根目录下，它的主要作用是定义全局的 fixture 和钩子函数，用于测试前的准备工作和测试后的清理工作。这些 fixture 和钩子函数会在测试执行的不同阶段自动运行，确保测试环境的一致性和测试结果的准确性。
- 钩子函数：提前埋好的 “触发点”，满足条件时自动执行，不用手动调用。

```python
@pytest.fixture(scope="session", autouse=True)
def clear_extract():
    # 禁用HTTPS告警
    warnings.simplefilter('ignore', ResourceWarning)
    # 清空yaml数据（extract.yaml）
    yfd.clear_yaml_data()
    # 清空测试报告目录下的所有文件
    remove_file("./report/temp", ['json', 'txt', 'attach', 'properties'])
```

**代码来源**：`Test-Automation-Framework-main/conftest.py`
**功能说明**：定义了一个session级别的自动执行fixture，用于在测试开始前清理测试环境，包括禁用HTTPS告警、清空extract.yaml数据和测试报告目录。

**测试前准备**：清空 extract.yaml 文件（用于存储接口提取的参数）和报告目录，确保测试环境干净，避免之前测试的数据残留影响当前测试。

**全局作用域**：通过 `scope="session"` 和 `autouse=True` 确保在整个测试会话中自动执行，无需手动调用，保证了测试的一致性。

### 3. 插件注册与钩子调用

**动作**：注册插件钩子，准备接管流程。

**核心触发**：通过 `config.hook.pytest_cmdline_main` 钩子介入主流程（可在此处打印版本信息或做早期参数检查）。

**细节**：

- 这个钩子是 pytest 内部执行测试流程的起点
- 它会利用之前创建的 `config` 对象，触发后续的测试收集（找到所有测试项）、执行（运行测试函数、管理 fixture）和报告（生成结果）等所有阶段
- 所有你在 `args` 中指定的选项（如 `-s, -v, --alluredir, ./testcase`）都会在 `config` 对象中体现，并被 `pytest_cmdline_main` 及其调用的后续流程使用
- `pytest_cmdline_main` 钩子执行完毕后会返回一个结果（通常是整数形式的退出码）将这个结果包装成 `ExitCode` 枚举类型（或保持为整数）并返回
- 这个退出码表示了测试运行的最终状态，`0` 通常表示所有测试通过（`ExitCode.OK`）
- 非 `0` 值表示有测试失败、执行错误或其他问题（如 `ExitCode.TESTS_FAILED`, `ExitCode.INTERRUPTED`, `ExitCode.USAGE_ERROR` 等）

### 4. 测试收集与参数化

测试用例解析与参数化阶段是测试执行的核心输入处理阶段，主要负责发现、加载和解析测试用例，为后续的测试执行做好准备。这个阶段的工作包括：发现测试用例文件、解析 YAML 格式的测试用例、处理参数化和变量替换等。

**动作**：递归扫描 `testcase` 目录（pytest.ini里面有写），收集符合命名规则的测试文件/函数。

**参数化**：

- 解析 `@pytest.mark.parametrize`
- 解析 YAML 数据源，动态生成多个测试实例（实现数据驱动）

**结果**：生成测试收集报告（Collection Report），确定要运行的测试节点列表。

#### **4.1用例发现与加载**：

- **文件路径**：`Test-Automation-Framework-main/common/readyaml.py`
- **YAML 用例文件结构**：

```plain
- baseInfo:
    api_name: "用户登录"
    url: "/api/login"
    method: "POST"
    header: {"Content-Type": "application/json"}
  testCase:
  - case_name: "正常登录"
    data: {"username": "admin", "password": "123456"}
    validation: "{\"status_code\": 200, \"has_token\": True}"
    extract: {"token": "$.data.token"}
```

- **用例读取核心代码**：**文件路径**：`Test-Automation-Framework-main/common/readyaml.py`

```python
import yaml
from common.recordlog import logs  # 这句你源码里没写，但必须要有
def get_testcase_yaml(file):
    """
    读取YAML格式的测试用例文件，解析成pytest参数化需要的数据格式
    返回格式：[[baseInfo, testCase1], [baseInfo, testCase2], ...]
    """
    # 初始化一个空列表，用于存储最终返回的测试用例数据
    testcase_list = []
    try:
        # 打开YAML文件，使用只读模式，编码utf-8防止中文乱码
        with open(file, 'r', encoding='utf-8') as f:
            # 安全加载YAML文件内容，转换为Python列表/字典
            data = yaml.safe_load(f)
            # 判断YAML数据长度：如果数据长度 <=1，表示是标准单接口多用例格式
            if len(data) <= 1:
                # 取出YAML里第1组数据（baseInfo + testCase都在这里）
                yam_data = data[0]
                # 提取公共的基础信息：url、域名、请求头、接口地址等
                base_info = yam_data.get('baseInfo')
                # 遍历提取每一条测试用例（testCase下的所有用例）
                for ts in yam_data.get('testCase'):
                    # 把公共信息base_info 和 单条用例ts 打包成一个列表
                    param = [base_info, ts]
                    # 将打包好的参数添加到测试用例列表中
                    testcase_list.append(param)
                # 返回处理好的参数化列表，给@pytest.mark.parametrize使用
                return testcase_list
            else:
                # 如果YAML数据不是标准格式，直接返回原始数据
                return data
    # 如果读取文件过程中出现异常（文件不存在、格式错误、权限问题）
    except Exception as e:
        # 记录错误日志，方便排查问题
        logs.error(f'获取【{file}】文件数据时出现未知错误: {str(e)}')
```

**功能说明**：数据读取与解析模块负责读取和解析测试用例中的数据，特别是处理 YAML 中的变量替换。它支持通过 `${}` 语法引用函数和变量，实现测试数据的动态生成和接口关联。

#### **4.2YAML 数据替换解析：**

```python
def replace_load(self, data):
    """yaml数据替换解析：用于替换 YAML 中的 ${函数名(参数)} 格式变量"""
    # 把传入的 data 赋值给 str_data，先默认当成字符串处理
    str_data = data  
    # 如果 data 不是字符串（比如字典、列表），就转成 JSON 字符串
    if not isinstance(data, str):
        str_data = json.dumps(data, ensure_ascii=False)  
    # 循环查找字符串里有多少个 ${，有几个就循环替换几次
    for i in range(str_data.count('${')):
        # 确保字符串中同时存在 ${ 和 }
        if '${' in str_data and '}' in str_data:
            # 找到 ${ 的起始位置
            start_index = str_data.index('$')
            # 找到从起始位置开始，第一个 } 的位置
            end_index = str_data.index('}', start_index)            
            # 截取完整的占位符：比如 ${get_token(123)}
            ref_all_params = str_data[start_index:end_index + 1]          
            # 从占位符中取出函数名：截取 ${ 后面、( 前面的内容 → get_token
            func_name = ref_all_params[2:ref_all_params.index("(")]
            # 取出函数参数：截取 ( 和 ) 之间的内容 → 123
            func_params = ref_all_params[ref_all_params.index("(") + 1:ref_all_params.index(")")]        
            # 使用反射调用 DebugTalk 类里的函数，并传入参数
            # 如果有参数就按逗号分割，没有参数就传空
            extract_data = getattr(DebugTalk(), func_name)(*func_params.split(',') if func_params else "")        
            # 如果返回的是列表，转成逗号拼接的字符串
            if extract_data and isinstance(extract_data, list):
                extract_data = ','.join(e for e in extract_data)            
            # 把原来的 ${xxx} 替换成执行函数后得到的真实值
            str_data = str_data.replace(ref_all_params, str(extract_data))    
    # 替换完成后，还原数据格式
    if data and isinstance(data, dict):
        # 如果原来的数据是字典，就把字符串转回字典
        data = json.loads(str_data)
    else:
        # 否则直接用字符串
        data = str_data   
    # 返回替换完成后的最终数据
    return data
```

**代码来源**：`Test-Automation-Framework-main/base/apiutil.py`
**功能说明**：用于替换YAML中的${函数名(参数)}格式变量，支持调用DebugTalk类中的方法来生成动态数据，如获取随机数、时间戳、提取之前接口的返回值等。

说明：该函数会将输入的数据转换为字符串，然后查找并替换其中的 `${}` 表达式。它支持调用 DebugTalk 类中的方法来生成动态数据，如获取随机数、时间戳、提取之前接口的返回值等。替换完成后，它会将数据还原为原始类型（如字典或字符串）并返回**。**

#### **4.3参数化处理**：

- **Python 测试文件中的参数化**：

```python
# 导入pytest测试框架，用来管理和执行测试用例
import pytest
# 导入自己封装的YAML数据驱动工具：读取yaml文件中的测试数据
from common.readyaml import get_testcase_yaml
# 导入自己封装的接口请求基类：负责发送请求、断言、结果处理
from base.apiutil import RequestBase

# ------------------- 核心：数据驱动 +  parametrize 参数化 -------------------
# @pytest.mark.parametrize：pytest数据驱动装饰器
# "base_info, test_case"：定义传入测试函数的两个参数
# get_testcase_yaml(...)：从yaml文件读取登录接口的测试数据
@pytest.mark.parametrize("base_info, test_case", get_testcase_yaml("./testcase/Single interface/test_ecommerce_login.yaml"))
def test_login(base_info, test_case):
    """
    电商登录接口测试用例
    :param base_info: yaml文件中的公共基础信息（域名、请求头、接口地址等）
    :param test_case: yaml文件中的单条测试用例（请求参数、用例名称、预期结果等）
    """
    # 调用封装好的接口请求方法
    # 传入基础配置 + 测试用例数据
    # 内部自动完成：发送请求 → 响应断言 → 结果返回
    RequestBase().specification_yaml(base_info, test_case)
```

**代码来源**：`Test-Automation-Framework-main/testcase/Single interface/test_ecommerce_login.py`
**功能说明**：使用pytest的参数化装饰器，从YAML文件中读取测试数据，生成多个测试实例，实现数据驱动测试。

![img](https://cdn.nlark.com/yuque/0/2026/png/42530731/1775385675569-fe1f1bef-676e-49c0-9554-b9e28e7a0a16.png)

**说明**：参数化处理是实现数据驱动测试的关键。通过这种方式，测试用例数据与测试代码分离，使得测试用例的维护和管理更加方便。同时，它也使得测试框架能够自动生成多个测试实例，提高测试的覆盖率和效率。

### 5. 环境准备与前置处理

**动作**：开始执行测试循环，准备运行环境。

**全局清理（Session级）**：

- 触发 `scope="session"` 且 `autouse=True` 的 Fixture（如 `clear_extract`）
- **逻辑**：清空临时 YAML 数据、删除旧报告文件，确保环境纯净

**业务前置（Module/Function级）**：

- 针对具体测试用例，执行依赖的 Fixture（如 `system_login`）
- **逻辑**：执行登录操作，获取 Token/Cookie 并注入到请求头中

### 6. 核心流程执行

**动作**：调度器（`runtestloop`）逐个运行测试用例。

#### **6.1：构建请求**

- 调用 `RequestBase().specification_yaml()`，根据用例数据构建 HTTP 请求对象
- **核心执行方法**：

```python
def specification_yaml(self, base_info, test_case):
    """
    接口请求处理核心方法（从yaml读取数据 → 发送请求 → 断言）
    :param base_info: 接口公共信息（url、method、header等）
    :param test_case: 单条测试用例（参数、断言、提取等）
    """
    # 1. 捕获异常，保证接口报错不会导致整个框架崩溃
    try:
        # 定义三种请求参数类型：表单data、json、url参数params
        params_type = ['data', 'json', 'params']
        # 从配置文件读取环境域名（如：http://test.xxx.com）
        url_host = self.conf.get_section_for_data('api_envi', 'host')
        # 从base_info获取接口名称
        api_name = base_info['api_name']
        # 把接口名称附加到 Allure 报告里
        allure.attach(api_name, f'接口名称：{api_name}', allure.attachment_type.TEXT)
        # 拼接完整请求地址：域名 + 接口路径
        url = url_host + base_info['url']
        # 把完整URL附加到 Allure 报告
        allure.attach(api_name, f'接口地址：{url}', allure.attachment_type.TEXT)
        # 获取请求方法 GET/POST/PUT/DELETE
        method = base_info['method']
        allure.attach(api_name, f'请求方法：{method}', allure.attachment_type.TEXT)
        # 读取请求头，并执行替换（如替换token、变量）
        header = self.replace_load(base_info['header'])
        allure.attach(api_name, f'请求头：{header}', allure.attachment_type.TEXT)
        # 处理 cookie（如果有）
        cookie = None
        if base_info.get('cookies') is not None:
            # 替换变量 → 转成字典
            cookie = eval(self.replace_load(base_info['cookies']))
        # 从用例中取出用例名称（并从用例字典删掉）
        case_name = test_case.pop('case_name')
        allure.attach(api_name, f'测试用例名称：{case_name}', allure.attachment_type.TEXT)
        # 处理断言：替换变量 ${token} 这类
        val = self.replace_load(test_case.get('validation'))
        test_case['validation'] = val
        # 把断言字符串转成字典/列表
        validation = eval(test_case.pop('validation'))
        # 处理参数提取（extract、extract_list）
        extract = test_case.pop('extract', None)
        extract_list = test_case.pop('extract_list', None)
        # 遍历处理请求参数（data/json/params）
        for key, value in test_case.items():
            # 如果是请求参数类型，就做变量替换
            if key in params_type:
                test_case[key] = self.replace_load(value)
        # 处理文件上传
        # 从用例中取出 files 字段
        file, files = test_case.pop('files', None), None
        if file is not None:
            # 遍历文件信息，附加到 Allure 报告
            for fk, fv in file.items():
                allure.attach(json.dumps(file), '导入文件')
                # 打开文件，准备上传
                files = {fk: open(fv, mode='rb')}
```

**代码来源**：`Test-Automation-Framework-main/base/apiutil.py`
**功能说明**：接口请求处理核心方法，负责从YAML读取数据，构建HTTP请求，发送请求，处理响应，执行断言等操作。

#### **6.2：发送与提取**

- 发送 HTTP 请求，获取响应
- **文件路径**：`Test-Automation-Framework-main/common/sendrequest.py`
- **功能说明**：请求发送实现模块负责发送 HTTP 请求，支持 GET、POST 等多种请求方法，处理文件上传、Cookie 等特殊情况，并记录请求和响应的详细信息。

```python
def run_main(self, name, url, case_name, method, header=None, file=None, cookies=None, **kwargs):
    """
    发送请求主方法
    :param name: 接口名称
    :param url: 接口地址
    :param case_name: 测试用例名称
    :param method: 请求方法
    :param header: 请求头
    :param file: 文件上传
    :param cookies: cookies
    :param kwargs: 其他参数
    :return: 响应对象
    """
    # 记录请求信息
    logs.info(f"接口名称：{name}")
    logs.info(f"测试用例：{case_name}")
    logs.info(f"请求地址：{url}")
    logs.info(f"请求方法：{method}")
    logs.info(f"请求头：{header}")
    logs.info(f"请求参数：{kwargs}")

    # 发送请求
    try:
        if method.upper() == 'GET':
            response = requests.get(url=url, params=kwargs.get('params'), headers=header, cookies=cookies, timeout=API_TIMEOUT)
        elif method.upper() == 'POST':
            if file:
                response = requests.post(url=url, data=kwargs.get('data'), files=file, headers=header, cookies=cookies, timeout=API_TIMEOUT)
            else:
                response = requests.post(url=url, data=kwargs.get('data'), json=kwargs.get('json'), headers=header, cookies=cookies, timeout=API_TIMEOUT)
        # 其他请求方法...

        # 记录响应信息
        logs.info(f"响应状态码：{response.status_code}")
        logs.info(f"响应内容：{response.text}")

        return response
    except Exception as e:
        logs.error(f"请求异常：{str(e)}")
        raise e

res = self.run.run_main(name=api_name, url=url, case_name=case_name, header=header, method=method,
                        file=files, cookies=cookie, **test_case)
# 获取接口响应的HTTP状态码（如200、404、500）
status_code = res.status_code
# 把接口响应数据以TEXT格式附加到Allure测试报告中，方便查看
allure.attach(self.allure_attach_response(res.json()), '接口响应信息', allure.attachment_type.TEXT)
# 捕获异常：处理接口返回结果和断言可能出现的错误
try:
    # 将接口返回的JSON字符串转换成Python字典，方便取值
    res_json = json.loads(res.text)   
    # 如果有需要提取的字段（extract不为空），就调用方法从响应中提取数据
    if extract is not None:
        self.extract_data(extract, res.text)    
    # 如果有需要提取的列表数据（extract_list不为空），就调用方法提取
    if extract_list is not None:
        self.extract_data_list(extract_list, res.text)    
    # 核心：执行断言，校验预期结果与实际响应、状态码是否一致
    self.asserts.assert_result(validation, res_json, status_code)
# 捕获JSON解析错误：说明接口返回不是合法JSON，可能是系统异常或请求失败
except JSONDecodeError as js:
    logs.error('系统异常或接口未请求！')
    # 抛出异常，让测试用例标记为失败
    raise js
# 捕获其他所有异常（如断言失败、提取数据失败等）
except Exception as e:
    # 打印错误日志
    logs.error(e)
    # 抛出异常，让测试用例标记为失败
    raise e
```

**代码来源**：`Test-Automation-Framework-main/common/sendrequest.py`
**功能说明**：发送请求主方法，支持GET、POST等多种请求方法，处理文件上传、Cookie等特殊情况，并记录请求和响应的详细信息。

- **变量替换与接口关联：**执行 `extract_data`，自动提取响应中的关键字段（如 ID、Token）存入全局变量池，供后续用例使用

```python
def extract_data(self, testcase_extarct, response):
    """
    提取接口的返回值，支持正则表达式和json提取器
    :param testcase_extarct: testcase文件yaml中的extract值
    :param response: 接口的实际返回值
    :return:
    """
    # 捕获异常，防止提取失败导致程序崩溃
    try:
        # 定义正则表达式的四种常用匹配模式，用于判断是否采用正则提取
        # 定义框架支持的 4 种正则提取表达式（用于从接口返回文本中提取数据）
        pattern_lst = [
            '(.*?)',   # 1. 匹配 任意字符（包括空），非贪婪匹配（最常用）
            '(.+?)',   # 2. 匹配 任意非空字符，至少一个，非贪婪匹配
            r'(\d)',   # 3. 匹配 单个数字（0-9）
            r'(\d*)'   # 4. 匹配 任意个数字（包括空），等价于 \d{0,}
        ]
        # 遍历yaml中extract定义的所有键值对，例如：{"token":"$.data.token","user_id":"user:(\\d+)"}
        for key, value in testcase_extarct.items():

            # ===================== 正则表达式提取 =====================
            # 循环判断当前提取规则是否包含正则表达式符号
            for pat in pattern_lst:
                # 如果提取规则中包含预定义的正则符号，则按正则方式提取
                if pat in value:
                    # 使用re.search在接口返回内容中匹配正则表达式，获取匹配结果对象
                    ext_lst = re.search(value, response)
                    # 判断是否为数字类型正则（匹配整数）
                    if pat in [r'(\d+)', r'(\d*)']:
                        # 将提取到的内容强转为int，并组成字典：{变量名: 提取值}
                        extract_data = {key: int(ext_lst.group(1))}
                    else:
                        # 非数字类型，直接提取字符串，组成字典
                        extract_data = {key: ext_lst.group(1)}
                    # 将提取好的变量写入yaml文件，保存为全局变量，供其他接口关联使用
                    self.read.write_yaml_data(extract_data)

            # ===================== JSONPath 提取（最常用） =====================
            # 如果提取规则中包含 $ 符号，说明是JSONPath提取
            if '$' in value:
                # 将接口返回的字符串转成json对象，并用jsonpath提取对应字段，[0]取第一个结果
                ext_json = jsonpath.jsonpath(json.loads(response), value)[0]
                # 判断是否成功提取到数据
                if ext_json:
                    # 提取成功，组成字典
                    extarct_data = {key: ext_json}
                    logs.info('提取接口的返回值：', extarct_data)
                else:
                    # 提取失败，给出提示信息
                    extarct_data = {key: '未提取到数据，请检查接口返回值是否为空！'}
                # 将提取到的变量写入yaml文件，实现接口关联
                self.read.write_yaml_data(extarct_data)
    
    # 捕获所有异常，打印错误日志，不中断测试流程
    except Exception as e:
        logs.error(e)
def extract_data_list(self, testcase_extract_list, response):
    """
    提取多个参数，支持正则表达式和json提取，提取结果以列表形式返回
    :param testcase_extract_list: yaml文件中的extract_list信息
    :param response: 接口的实际返回值,str类型
    :return:
    """
    try:
        # 遍历 extract_list 里所有要提取的字段（如 { "id_list": "$..id", "name_list": "name:(.+?)" }）
        for key, value in testcase_extract_list.items():

            # ===================== 正则批量提取（列表） =====================
            # 判断提取规则是否包含正则符号：(.+?) 或 (.*?)，包含就走正则提取
            if "(.+?)" in value or "(.*?)" in value:
                # re.findall：提取**所有匹配项**，返回列表格式（re.S 表示跨行匹配）
                ext_list = re.findall(value, response, re.S)
                # 如果提取到内容
                if ext_list:
                    # 组装成字典：{变量名: [值1, 值2, 值3...]}
                    extract_date = {key: ext_list}
                    logs.info('正则提取到的参数：%s' % extract_date)
                    # 写入 extract.yaml 保存为全局变量
                    self.read.write_yaml_data(extract_date)

            # ===================== JSONPath 批量提取（列表） =====================
            # 如果规则包含 $，代表是 JSONPath 提取
            if "$" in value:
                # jsonpath.jsonpath 提取所有匹配结果，返回列表（支持 $..id 这种递归提取）
                ext_json = jsonpath.jsonpath(json.loads(response), value)
                # 判断是否提取到数据
                if ext_json:
                    extract_date = {key: ext_json}
                else:
                    extract_date = {key: "未提取到数据，该接口返回结果可能为空"}
                
                logs.info('json提取到参数：%s' % extract_date)
                # 写入 extract.yaml 供其他接口使用
                self.read.write_yaml_data(extract_date)

    # 提取失败捕获异常
    except:
        logs.error('接口返回值提取异常，请检查yaml文件extract_list表达式是否正确！')
def write_yaml_data(self, value):
    """
    写入数据需为dict，allow_unicode=True表示写入中文，sort_keys按顺序写入
    写入YAML文件数据,主要用于接口关联
    """
    # 获取要写入的 yaml 文件路径（extract.yaml，专门存提取出来的变量）
    file_path = FILE_PATH['EXTRACT']
    # 创建文件所在的目录，如果目录已存在则不报错（exist_ok=True）
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # 初始化文件对象，防止finally中关闭未打开的文件报错
    file = None
    try:
        # 以 追加模式 打开yaml文件（a = append，不会覆盖原有内容）
        file = open(file_path, 'a', encoding='utf-8')
        # 判断传入的值是不是字典格式（yaml只能写入字典）
        if isinstance(value, dict):
            # 将字典转成yaml格式的字符串
            # allow_unicode=True：支持写入中文不乱码
            # sort_keys=False：不按key排序，保持原来的顺序
            write_data = yaml.dump(value, allow_unicode=True, sort_keys=False)

            # 把转换好的内容写入文件
            file.write(write_data)
        else:
            # 如果不是字典，打印提示信息
            logs.info('写入[extract.yaml]的数据必须为dict格式')
    # 捕获所有异常，打印错误堆栈日志
    except Exception:
        logs.error(str(traceback.format_exc()))
    # 无论是否异常，最终都会执行：关闭文件，释放资源
    finally:
        # 如果文件已打开，则关闭
        if file:
            file.close()
```

**代码来源**：`Test-Automation-Framework-main/base/apiutil.py`（extract_data和extract_data_list）、`Test-Automation-Framework-main/common/readyaml.py`（write_yaml_data）
**功能说明**：extract_data和extract_data_list用于从接口响应中提取数据，支持正则表达式和JSONPath两种提取方式；write_yaml_data用于将提取的数据写入extract.yaml文件，实现接口关联。

- **变量引用**：在 YAML 用例中使用 `${}` 语法引用已提取的变量，如 `${get_extract('token')}`

**说明**：变量替换与接口关联是实现复杂测试场景的关键。通过这种方式，测试框架可以处理接口之间的依赖关系，如登录接口返回的 token 可以被后续的接口使用，实现完整的业务流程测试。同时，它也使得测试用例更加灵活和可维护。

**说明**：数据提取是实现接口关联的关键。通过正则表达式或 JSONPath，测试框架可以根据规则从接口响应中提取需要的数据，如 token、用户 ID 等，然后存储到 extract.yaml 文件中。后续的测试用例可以通过变量引用使用这些数据，实现接口之间的依赖关系。

#### **6.3：断言与日志**

**文件路径**：`Test-Automation-Framework-main/common/assertions.py`

**功能说明**：断言执行模块负责验证接口响应是否符合预期，支持多种断言类型，如状态码断言、包含断言、存在断言等。如果断言失败，它会记录详细的错误信息，方便问题定位。

- 执行断言（`assert` 或自定义断言方法），验证响应结果

```python
self.asserts.assert_result(validation, res_json, status_code)
```

- 记录请求 URL、参数、响应结果及断言状态到日志系统
- **断言核心实现**：

```python
class Assertions:
    def assert_result(self, validation, response, status_code):
        """
        断言结果
        :param validation: 断言规则
        :param response: 响应数据
        :param status_code: 状态码
        :return:
        """
        try:
            # 状态码断言
            if 'status_code' in validation:
                assert status_code == validation['status_code'], f"状态码断言失败，期望：{validation['status_code']}，实际：{status_code}"

            # 包含断言
            if 'contains' in validation:
                for key, value in validation['contains'].items():
                    assert key in response, f"响应中未包含字段：{key}"
                    assert response[key] == value, f"字段值断言失败，字段：{key}，期望：{value}，实际：{response[key]}"

            # 存在断言
            if 'has_token' in validation:
                assert 'token' in response.get('data', {}), "响应中未包含 token"

            # 其他断言类型...

            logs.info("断言成功！")
        except AssertionError as e:
            logs.error(f"断言失败：{str(e)}")
            raise e
        except Exception as e:
            logs.error(f"断言过程中出现异常：{str(e)}")
            raise e
```

**代码来源**：`Test-Automation-Framework-main/common/assertions.py`
**功能说明**：断言执行模块负责验证接口响应是否符合预期，支持多种断言类型，如状态码断言、包含断言、存在断言等。如果断言失败，它会记录详细的错误信息，方便问题定位。

### 7. 结果统计与通知

**功能说明**：报告埋点与结果记录模块负责记录测试过程中的详细信息，生成测试报告，包括添加 Allure 报告附件、收集测试结果、生成测试摘要等操作。这些操作确保了测试报告的完整性和可读性，方便测试人员和开发人员查看测试结果和定位问题。

**动作**：所有用例执行完毕，进入总结阶段。

**钩子**：通过 `pytest_terminal_summary` 钩子收集最终结果。

**统计**：计算通过数、失败数、跳过数、耗时等。

**通知**：若配置开启，调用钉钉/企业微信接口发送测试报告卡片。

**Allure 报告附件**：

```python
# 在 apiutil.py 中
def allure_attach_response(cls, response):
    """
    统一处理接口响应数据，格式化后用于展示在 Allure 报告中
    作用：让响应体在报告里排版美观、不乱码、支持中文
    :param response: 接口返回的原始响应（dict 或 str）
    :return: 格式化好的字符串
    """
    # 判断响应数据是不是字典（一般是接口返回的 JSON）
    if isinstance(response, dict):
        # 如果是字典 → 转成格式化 JSON 字符串
        # ensure_ascii=False：支持中文，不转成 Unicode 编码
        # indent=4：缩进4个字符，报告里看起来更整齐美观
        allure_response = json.dumps(response, ensure_ascii=False, indent=4)
    else:
        # 如果不是字典（如纯文本、HTML、XML），直接使用原数据
        allure_response = response
    # 返回格式化好的数据，用于附加到 Allure 报告
    return allure_response
# ===================== 以下是添加附件到 Allure 报告的示例 =====================
# 附加：接口名称
allure.attach(api_name, f'接口名称：{api_name}', allure.attachment_type.TEXT)
# 附加：接口地址 URL
allure.attach(api_name, f'接口地址：{url}', allure.attachment_type.TEXT)
# 附加：请求方法 GET/POST/PUT/DELETE
allure.attach(api_name, f'请求方法：{method}', allure.attachment_type.TEXT)
# 附加：请求头 headers
allure.attach(api_name, f'请求头：{header}', allure.attachment_type.TEXT)
# 附加：接口响应信息（调用上面的方法格式化后再展示）
allure.attach(self.allure_attach_response(res.json()), '接口响应信息', allure.attachment_type.TEXT)
```

**代码来源**：`Test-Automation-Framework-main/base/apiutil.py`
**功能说明**：统一处理接口响应数据，格式化后用于展示在 Allure 报告中，使响应体在报告里排版美观、不乱码、支持中文。

**测试结果收集**：

```python
# 导入time模块（代码里没写，但必须要有，用于计算执行时间）
import time
# 在 conftest.py 中
def generate_test_summary(terminalreporter):
    """
    生成测试结果摘要字符串
    作用：统计pytest运行后的所有用例结果（总数、通过、失败、跳过、耗时）
    :param terminalreporter: pytest内置的测试结果报告对象（自带统计数据）
    :return: 拼接好的测试结果字符串
    """
    # 获取【总共收集到的测试用例数量】
    total = terminalreporter._numcollected  
    # 获取【通过的用例数】：从stats字典中取passed列表，计算长度
    passed = len(terminalreporter.stats.get('passed', []))  
    # 获取【失败的用例数】（断言失败）
    failed = len(terminalreporter.stats.get('failed', []))    
    # 获取【错误用例数】（代码报错、框架异常）
    error = len(terminalreporter.stats.get('error', [])) 
    # 获取【跳过执行的用例数】
    skipped = len(terminalreporter.stats.get('skipped', []))
    # 计算【执行总耗时】：当前时间 - 测试会话开始时间
    duration = time.time() - terminalreporter._sessionstarttime
    # 拼接成一段友好的通知文本（用于钉钉/企业微信/邮件通知）
    summary = f"""
    自动化测试结果，通知如下，请着重关注测试失败的接口，具体执行结果如下：
    测试用例总数：{total}
    测试通过数：{passed}
    测试失败数：{failed}
    错误数量：{error}
    跳过执行数量：{skipped}
    执行总时长：{duration:.2f}秒  # 加了:.2f让时间只显示2位小数，更好看
    """
    # 打印结果到控制台
    print(summary)
    # 返回统计结果，给发送通知的函数使用
    return summary
```

**代码来源**：`Test-Automation-Framework-main/conftest.py`
**功能说明**：生成测试结果摘要字符串，统计pytest运行后的所有用例结果（总数、通过、失败、跳过、耗时），用于钉钉/企业微信/邮件通知。

**通知发送**：

```plain
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """pytest钩子函数：测试全部结束后自动执行"""
    summary = generate_test_summary(terminalreporter)
    if dd_msg:
        send_dd_msg(summary)  # 如果配置里开了钉钉通知，就发消息
```

**代码来源**：`Test-Automation-Framework-main/conftest.py`
**功能说明**：pytest钩子函数，测试全部结束后自动执行，用于生成测试结果摘要并发送通知。

### 8. 报告生成

**HTML 报告**：生成 `pytest-html` 报告（`--html=report.html`）。

**Allure 数据**：生成 Allure 原始数据（`--alluredir=./allure-results`）。

**Allure 静态页**：（可选）执行 `allure generate` 命令，将原始数据转换为可视化的 HTML 报告。

**报告生成实现**：

- **Allure 报告生成**：

```plain
if REPORT_TYPE == 'allure':
    pytest.main([
    '-s', '-v',            # 输出详细日志
    '--alluredir=./report/temp',  # 把测试结果存到 temp 目录
    './testcase',          # 运行 testcase 下所有用例
    '--clean-alluredir',   # 运行前清空旧报告
    '--junitxml=./report/results.xml'  # 生成JUnit格式结果
])

    shutil.copy('./environment.xml', './report/temp') # 复制环境配置文件到报告目录
    os.system('allure serve ./report/temp')
```

**代码来源**：`Test-Automation-Framework-main/run.py`
**功能说明**：生成Allure报告，包括运行测试用例、生成测试结果、复制环境配置文件、启动Allure服务展示报告。

- **TM 报告生成**：

```plain
elif REPORT_TYPE == 'tm':
    pytest.main(['-vs', '--pytest-tmreport-name=testReport.html', '--pytest-tmreport-path=./report/tmreport'])
    webbrowser.open_new_tab(os.getcwd() + '/report/tmreport/testReport.html')
```

**代码来源**：`Test-Automation-Framework-main/run.py`
**功能说明**：生成TM报告，包括运行测试用例、生成测试结果、自动打开报告页面。

### 9. 收尾清理

**动作**：释放资源，结束会话。

**Fixture 清理**：执行 `session` 级 Fixture 的 `yield` 后方代码或 `finalizer`（如 `ensure_unconfigure`）。

**资源释放**：关闭数据库连接、关闭 HTTP 连接池、清理临时文件。

**资源清理实现**：

- **测试报告目录清理**：

```plain
# 在 conftest.py 中
def clear_extract():
    # 清空测试报告目录下的所有文件
    remove_file("./report/temp", ['json', 'txt', 'attach', 'properties'])
```

**代码来源**：`Test-Automation-Framework-main/conftest.py`
**功能说明**：清空测试报告目录下的所有文件，确保每次测试都是在干净的环境中进行。

- **extract.yaml 清理**：

```plain
# 在 common/readyaml.py 中
def clear_yaml_data(self):
    """
    清空extract.yaml文件数据
    :param filename: yaml文件名
    :return:
    """
    with open(FILE_PATH['EXTRACT'], 'w') as f:
        f.truncate()
```

**代码来源**：`Test-Automation-Framework-main/common/readyaml.py`
**功能说明**：清空extract.yaml文件数据，确保每次测试都是在干净的环境中进行。

### 10. 程序结束

**动作**：`run.py` 接收 `pytest` 返回的退出码（Exit Code）。

**结果**：0 表示全通过，非 0 表示有失败，进程结束并将状态返回给操作系统（用于 CI/CD 判定）。

### 💡 流程图解关键路径

为了让你更直观地理解，核心路径可以简化为：

```plain
main() ➔ 配置 ➔ 收集(参数化) ➔ Session Fixture(清空) ➔ 循环测试 ➔ Func Fixture(登录) ➔ 业务逻辑(请求/断言) ➔ Fixture Teardown(清理) ➔ Summary(统计/报告) ➔ Exit
```

## 3. 项目总结

**项目特点**：

- **数据驱动**：使用 YAML 文件存储测试用例，支持参数化测试
- **接口关联**：通过 `extract.yaml` 实现接口之间的数据传递
- **灵活断言**：支持多种断言类型，验证接口响应
- **丰富报告**：支持 Allure 和 TM 两种报告类型，可视化展示测试结果
- **自动化通知**：支持钉钉机器人发送测试结果通知
- **易于扩展**：模块化设计，便于添加新功能

**核心流程**：

1. **初始化与配置**：加载配置文件，初始化测试环境
2. **测试收集与参数化**：发现测试用例，处理参数化
3. **环境准备**：执行前置 Fixture，清理环境
4. **核心执行**：发送接口请求，处理响应，执行断言
5. **结果处理**：收集测试结果，生成报告，发送通知
6. **资源清理**：释放资源，结束会话

**技术栈**：

- **测试框架**：pytest
- **HTTP 客户端**：requests
- **报告工具**：Allure
- **数据存储**：YAML
- **日志系统**：logging

通过这个项目，测试人员可以快速编写和执行接口测试用例，自动化验证接口功能，提高测试效率和质量。同时，项目的模块化设计也使得它易于维护和扩展，可以根据具体项目的需求进行定制。