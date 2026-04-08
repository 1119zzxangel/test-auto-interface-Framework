项目运行与代码说明
=================

一、项目简介
- 本项目是一个基于 Pytest 的接口自动化测试框架模板，使用 Python 语言实现，集成了 YAML 用例驱动、请求发送、结果断言、用例间数据提取、以及 Allure/tm 报告生成与钉钉通知等能力。
- 主要依赖见 `pyproject.toml`，推荐 Python >= 3.12 环境。

二、总体架构与逻辑原理
- 目录结构要点：
  - `base/`：框架底层工具与通用流程实现（例如：`apiutil.py` 请求/用例处理入口）。
  - `common/`：常用工具集（日志、读取 YAML、发送请求、断言、钉钉、读写 Excel 等）。
  - `conf/`：配置项与路径定义（例如：`setting.py`、`operationConfig.py`）。
  - `testcase/`：YAML 或其它格式的测试用例目录（按业务模块组织）。
  - `report/`：测试执行生成的报告与临时文件。

- 关键流程（高层次）：
  1. 用例编写：测试用例以 YAML 为主，包含 `baseInfo`（接口元信息）与 `testCase`（单条用例），见 `common/readyaml.py` 的读取格式。
  2. 执行入口：运行 `run.py` 或使用 `pytest` 直接执行 `testcase` 目录下用例；运行时由 `conftest.py` 做会话级初始化（清理 extract、临时文件、钉钉开关等）。
  3. 用例运行：`base/apiutil.py`（类 `RequestBase`）负责：解析 YAML、变量替换（支持调用 `common/debugtalk.py` 中的自定义方法）、构造请求参数、调用 `common/sendrequest.py` 发送请求、提取返回值并写入 `extract.yaml`（用于用例链路间传参）、断言结果并上 Allure 附件。
  4. 请求发送：`common/sendrequest.py` 封装了 `requests` 的调用，统一记录日志、处理 Cookie、超时和异常，并返回原始 `requests.Response` 给上层处理。
  5. 报告与通知：根据 `conf/setting.py` 中的 `REPORT_TYPE` 决定 Allure 或 tm 风格报告；执行结束后可通过 `run.py` 自动启动 `allure serve` 或打开 tm 报告；若在 `conftest.py` 中开启 `dd_msg`，会在结束时发送测试摘要到钉钉。

三、主要模块说明（要点）
- `run.py`：项目运行入口，依据 `REPORT_TYPE` 选择 Allure 或 tm 报告生成并展示。
- `base/apiutil.py`：核心调度类 `RequestBase`，实现：YAML 占位符替换、参数处理、上传文件支持、提取（正则或 jsonpath）、断言调用与 Allure 附件写入。
- `common/sendrequest.py`：HTTP 请求封装类 `SendRequest`，提供 `run_main()` 作为统一入口，内部使用 `requests.session()` 并处理 Cookie、日志与异常。
- `common/readyaml.py`：读取/写入 YAML 用例数据和 `extract.yaml` 的工具类 `ReadYamlData`，以及 `get_testcase_yaml()` 辅助函数用于解析单个 YAML 文件为多条用例。
- `conf/setting.py`：全局常量及路径定义（如 `FILE_PATH`、`API_TIMEOUT`、`REPORT_TYPE` 等），是调试与运行的重要开关点。
- `conftest.py`：Pytest 固件定义，如会话级清理 `clear_extract()` 和终端摘要回调 `pytest_terminal_summary()`（可发送钉钉消息）。

四、如何运行（快速上手）
1. 环境准备
   - 推荐 Python >= 3.12；建议在虚拟环境中运行（venv/conda）。
   - 安装依赖（在项目根目录运行）：

```bash
python -m pip install -U pip
python -m pip install -r requirements.txt || python -m pip install allure-pytest clickhouse-sqlalchemy jenkins jsonpath pandas paramiko pymongo pymysql pytest pyyaml redis requests sqlalchemy xlrd xlutils
```

   （备注：仓库包含 `pyproject.toml` 列出的依赖，可据此生成 `requirements.txt` 或直接安装。若使用 Poetry，请按 Poetry 流程安装。）

2. 配置（必要时）
   - 编辑 `conf/setting.py` 中的 `FILE_PATH`、`REPORT_TYPE`（`allure` 或 `tm`）、`API_TIMEOUT`、`dd_msg` 等常量以适配本地环境。
   - 如需对不同环境（测试/预发/生产）切换 host，可在项目中查找 `conf/operationConfig.py`（项目提供读取配置的封装），或直接修改 `conf/config.ini`。

3. 编写/组织用例
   - 在 `testcase/` 下按业务模块编写 YAML 用例，单个 YAML 文件结构参考 `common/readyaml.py` 中的解析逻辑：第一个元素为 `baseInfo`，后续为 `testCase` 列表。
   - 用例中支持变量替换语法 `${funcName(arg1,arg2)}`，会调用 `common/debugtalk.py` 中对应的函数并用返回值替换。
   - 用例支持字段：`data` / `json` / `params`（请求参数），`validation`（断言表达式），`extract` / `extract_list`（提取写入 `extract.yaml`）。

4. 运行测试
   - 直接运行 `run.py`（快速生成并启动报告，依赖 `REPORT_TYPE` 配置）：

```bash
python run.py
```

   - 或使用 pytest：

```bash
# 在项目根目录执行
pytest -vs ./testcase --alluredir=./report/temp
# 若使用 Allure，生成并查看报告
allure serve ./report/temp
```

5. 查看与清理
   - 临时文件和报告在 `report/` 下生成；`conftest.py` 的会话固件会在运行前清空 `extract.yaml` 并清理 `report/temp` 中的部分临时文件。

五、调试与常见注意事项
- YAML 编码：请确保 YAML 文件为 UTF-8 编码，否则 `common/readyaml.py` 会报编码错误。
- 断言与验证：`validation` 字段会被 `eval` 解析为 Python 表达式，请在编写时注意安全与正确性。
- 依赖与版本：若出现第三方依赖版本不兼容，优先参考 `pyproject.toml` 中的版本要求。
- Cookie 与提取：如果用例链路依赖上一步的返回值，请在上一步使用 `extract` 写入键名，然后在后续用例通过 `${}` 或 `ReadYamlData.get_extract_yaml()` 获取。
- 日志与报错：框架通过 `common/recordlog.py` 记录日志，查看 `logs` 目录下输出以定位异常。

六、可扩展方向（建议）
- 增加更完善的参数化支持（CSV/Excel/数据库驱动数据）。
- 增强并发执行能力与节流控制，避免过多并行请求导致服务器拒绝或本地资源耗尽。
- 将断言与提取器扩展为插件式策略，便于业务自定义扩展。
- 将配置与环境信息抽象为多环境支持（如 YAML 或 env 文件），便于 CI 集成。

七、参考文件
- 运行入口与报告逻辑：`run.py`
- 用例解析与执行：`base/apiutil.py`
- 请求封装：`common/sendrequest.py`
- YAML 读写：`common/readyaml.py`
- 全局配置：`conf/setting.py`
- 固件与报告摘要：`conftest.py`

如果你希望，我可以：
- 生成 `requirements.txt`（基于 `pyproject.toml`），
- 或者把 README_run.md 翻译为英文或转换为更详细的开发者文档。
