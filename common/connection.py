import traceback                          # 导入异常追踪模块
import clickhouse_sqlalchemy              # 导入ClickHouse数据库驱动
import pymysql                            # 导入MySQL数据库连接库
import redis                              # 导入Redis数据库连接库
import sys                                # 导入系统内置模块
import pymongo                            # 导入MongoDB数据库驱动
import paramiko                           # 导入SSH远程连接工具库
import pandas as pd                       # 导入数据处理库Pandas
from clickhouse_sqlalchemy import make_session  # 导入ClickHouse会话创建方法
from sqlalchemy import create_engine       # 导入SQLAlchemy引擎创建方法
from conf.operationConfig import OperationConfig  # 导入配置读取类
from common.recordlog import logs         # 导入自定义日志工具
from common.two_dimension_data import print_table  # 导入表格打印工具

conf = OperationConfig()                   # 创建配置文件操作对象

class ConnectMysql:
    def __init__(self):
        mysql_conf = {
            'host': conf.get_section_mysql('host'),        # 读取MySQL主机地址
            'port': int(conf.get_section_mysql('port')),    # 读取MySQL端口并转整型
            'user': conf.get_section_mysql('username'),     # 读取MySQL用户名
            'password': conf.get_section_mysql('password'), # 读取MySQL密码
            'database': conf.get_section_mysql('database')  # 读取MySQL数据库名
        }

        try:
            self.conn = pymysql.connect(**mysql_conf, charset='utf8')  # 创建MySQL连接
            self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)  # 创建字典游标
            # 避免在日志中打印敏感信息
            logs.info(f"成功连接到mysql---host：{mysql_conf['host']}，port：{mysql_conf['port']}，db：{mysql_conf['database']}")
        except Exception as e:
            logs.error(f"except:{e}")  # 捕获异常并打印错误日志
            raise

    def close(self):
        try:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()         # 关闭游标
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()           # 关闭数据库连接
            return True                     # 返回关闭结果
        except Exception as e:
            logs.error(f"关闭连接失败：{e}")
            return False

    def query_all(self, sql):
        if not isinstance(sql, str) or not sql:
            raise ValueError("SQL语句必须是非空字符串")
        
        try:
            self.cursor.execute(sql)    # 执行SQL语句
            res = self.cursor.fetchall() # 获取所有查询结果

            if not res:
                return []
                
            # 提取字段名和数据
            keys = list(res[0].keys()) if res else []
            values = [list(item.values()) for item in res]
            
            # 返回所有数据
            return values
        except Exception as e:
            logs.error(f"查询失败：{e}")
            raise
        finally:
            self.close()                 # 最终关闭连接

    def delete(self, sql):
        if not isinstance(sql, str) or not sql:
            raise ValueError("SQL语句必须是非空字符串")
            
        try:
            self.cursor.execute(sql)     # 执行删除SQL
            self.conn.commit()           # 提交事务
            logs.info('删除成功')        # 打印删除成功日志
            return True
        except Exception as e:
            logs.error(f"删除失败：{e}")
            self.conn.rollback()  # 回滚事务
            raise
        finally:
            self.close()                 # 关闭数据库连接

class ConnectRedis:
    def __init__(self, ip=conf.get_section_redis("host"), port=conf.get_section_redis("port"), username=None, passwd=None, db=conf.get_section_redis("db")):
        self.host = ip                   # 赋值Redis主机
        self.port = port                 # 赋值Redis端口
        self.username = username         # 赋值Redis用户名
        self.password = passwd           # 赋值Redis密码
        self.db = db                     # 赋值Redis库号
        # 避免在日志中打印敏感信息
        logs.info(f"连接Redis--host:{ip},port:{port},user:{username},db:{db}")  # 打印连接日志

        try:
            pool = redis.ConnectionPool(host=self.host, port=int(self.port), password=self.password)  # 创建连接池
            self.first_conn = redis.Redis(connection_pool=pool, decode_responses=True)  # 创建Redis连接
        except Exception as e:
            logs.error(f"连接Redis失败：{str(traceback.format_exc())}")  # 打印异常堆栈
            raise

    def close(self):
        try:
            if hasattr(self, 'first_conn') and self.first_conn:
                self.first_conn.close()
            return True
        except Exception as e:
            logs.error(f"关闭Redis连接失败：{e}")
            return False

    def set_kv(self, key, value, ex=None):
        """
        设置字符串键值对
        :param key: 键名
        :param value: 键值
        :param ex: 过期时间（秒）
        :return: 设置结果
        """
        if not key:
            raise ValueError("键名不能为空")
        try:
            return self.first_conn.set(name=key, value=value, ex=ex)  # 设置字符串键值对
        except Exception as e:
            logs.error(f"设置键值对失败：{str(traceback.format_exc())}")  # 打印异常堆栈
            raise

    def get_kv(self, name):
        """
        根据key获取值
        :param name: 键名
        :return: 键值
        """
        if not name:
            raise ValueError("键名不能为空")
        try:
            return self.first_conn.get(name)  # 根据key获取值
        except Exception as e:
            logs.error(f"获取键值失败：{str(traceback.format_exc())}")  # 打印异常堆栈
            raise

    def hash_set(self, key, value, ex=None):
        if not key:
            raise ValueError("键名不能为空")
        if not isinstance(value, dict):
            raise ValueError("value必须是字典类型")
        try:
            return self.first_conn.hset(key, mapping=value)  # 设置哈希数据
        except Exception as e:
            logs.error(f"设置哈希数据失败：{str(traceback.format_exc())}")  # 打印异常堆栈
            raise

    def hash_hget(self, names, keys):
        if not names:
            raise ValueError("哈希表名不能为空")
        if not keys:
            raise ValueError("字段名不能为空")
        try:
            data = self.first_conn.hget(names, keys)  # 获取哈希字段值
            return data  # 返回结果
        except Exception as e:
            logs.error(f"获取哈希字段值失败：{str(traceback.format_exc())}")  # 打印异常堆栈
            raise

    def hash_hmget(self, name, keys, *args):
        if not name:
            raise ValueError("哈希表名不能为空")
        if not isinstance(keys, list):
            raise ValueError("keys应为列表")  # 参数类型校验
        try:
            return self.first_conn.hmget(name, keys, *args)  # 批量获取哈希字段
        except Exception as e:
            logs.error(f"批量获取哈希字段失败：{str(traceback.format_exc())}")  # 打印异常堆栈
            raise

class ConnectClickHouse:
    """
    clickhouse有两个端口，8123和9000,分别用于接收 http协议和tcp协议请求，管理后台登录用的8123(jdbc连接)，
    而程序连接clickhouse(driver连接)则需要使用9000端口。如果在程序中使用8123端口连接就会报错
    """
    def __init__(self):
        config = {
            'server_host': conf.get_section_clickhouse('host'),  # 读取CH主机
            'port': conf.get_section_clickhouse('port'),          # 读取CH端口
            'user': conf.get_section_clickhouse('username'),     # 读取CH用户名
            'password': conf.get_section_clickhouse('password'), # 读取CH密码
            'db': conf.get_section_clickhouse('db'),              # 读取CH库名
            'send_receive_timeout': conf.get_section_clickhouse('timeout')  # 读取超时时间
        }
        try:
            connection = 'clickhouse://{user}:{password}@{server_host}:{port}/{db}'.format(**config)  # 拼接连接串
            engine = create_engine(connection, pool_size=100, pool_recycle=3600, pool_timeout=20)  # 创建引擎
            self.session = make_session(engine)  # 创建CH会话
            # 避免在日志中打印敏感信息
            logs.info(f"成功连接到clickhouse--server_host：{config['server_host']}，port：{config['port']}，database：{config['db']}，timeout：{config['send_receive_timeout']}")
        except Exception as e:
            logs.error(f"连接ClickHouse失败：{str(traceback.format_exc())}")  # 打印异常堆栈
            raise

    def close(self):
        try:
            if hasattr(self, 'session') and self.session:
                self.session.close()
            return True
        except Exception as e:
            logs.error(f"关闭ClickHouse连接失败：{e}")
            return False

    def sql(self, sql):
        if not isinstance(sql, str) or not sql:
            raise ValueError("SQL语句必须是非空字符串")
            
        cursor = None
        try:
            cursor = self.session.execute(sql)  # 执行SQL
            fields = cursor._metadata.keys  # 获取字段名
            df = pd.DataFrame([dict(zip(fields, item)) for item in cursor.fetchall()])  # 转DataFrame
            return df  # 返回结果
        except clickhouse_sqlalchemy.exceptions.DatabaseException as e:
            logs.error(f'SQL语法错误，请检查SQL语句：{e}')  # 捕获SQL异常
            raise
        except Exception as e:
            logs.error(f"执行SQL失败：{e}")  # 打印其他异常
            raise
        finally:
            if cursor:
                cursor.close()  # 关闭游标
            self.close()  # 关闭会话

class ConnectMongo(object):
    def __init__(self):
        mg_conf = {
            'host': conf.get_section_mongodb("host"),      # 读取Mongo主机
            'port': int(conf.get_section_mongodb("port")),  # 读取Mongo端口
            'user': conf.get_section_mongodb("username"),  # 读取Mongo用户名
            'passwd': conf.get_section_mongodb("password"),# 读取Mongo密码
            'db': conf.get_section_mongodb("database")     # 读取Mongo库名
        }

        try:
            self.client = pymongo.MongoClient('mongodb://{user}:{passwd}@{host}:{port}/{db}'.format(**mg_conf))  # 创建客户端
            self.db = self.client[mg_conf['db']]  # 绑定数据库
            # 避免在日志中打印敏感信息
            logs.info(f"连接到MongoDB，ip:{mg_conf['host']}，port:{mg_conf['port']}，database：{mg_conf['db']}")  # 打印日志
        except Exception as e:
            logs.error(f"连接MongoDB失败：{e}")  # 打印异常
            raise

    def close(self):
        try:
            if hasattr(self, 'client') and self.client:
                self.client.close()
            return True
        except Exception as e:
            logs.error(f"关闭MongoDB连接失败：{e}")
            return False

    def use_collection(self, collection):
        if not collection:
            raise ValueError("集合名不能为空")
        try:
            collect_table = self.db[collection]  # 获取集合对象
            return collect_table  # 返回集合
        except Exception as e:
            logs.error(f"获取集合失败：{e}")
            raise

    def insert_one_data(self, data, collection):
        if not data:
            raise ValueError("数据不能为空")
        if not collection:
            raise ValueError("集合名不能为空")
        try:
            result = self.use_collection(collection).insert_one(data)  # 插入单条数据
            return result.inserted_id
        except Exception as e:
            logs.error(f"插入单条数据失败：{e}")
            raise

    def insert_many_data(self, documents, collection):
        if not isinstance(documents, list):
            raise TypeError("参数必须是一个非空的列表")  # 参数校验
        if not documents:
            raise ValueError("文档列表不能为空")
        if not collection:
            raise ValueError("集合名不能为空")
        try:
            result = self.use_collection(collection).insert_many(documents)  # 批量插入
            return result.inserted_ids
        except Exception as e:
            logs.error(f"批量插入数据失败：{e}")
            raise

    def query_one_data(self, query_parame, collection):
        if not isinstance(query_parame, dict):
            raise TypeError("查询参数必须为dict类型")  # 参数校验
        if not collection:
            raise ValueError("集合名不能为空")
        try:
            res = self.use_collection(collection=collection).find_one(query_parame)  # 查询单条
            return res
        except Exception as e:
            logs.error(f"查询单条数据失败：{e}")
            raise

    def query_all_data(self, collection, query_parame=None, limit_num=sys.maxsize):
        if not collection:
            raise ValueError("集合名不能为空")
        table = self.use_collection(collection)
        if query_parame is not None:
            if not isinstance(query_parame, dict):
                raise TypeError("查询参数必须为dict类型")
        try:
            query_results = table.find(query_parame).limit(limit_num)
            res_list = [res for res in query_results]
            return res_list
        except Exception as e:
            logs.error(f"查询所有数据失败：{e}")
            raise

    def update_collection(self, query_conditions, after_change, collection):
        if not isinstance(query_conditions, dict) or not isinstance(after_change, dict):
            raise TypeError("参数必须为dict类型")
        if not collection:
            raise ValueError("集合名不能为空")
        res = self.query_one_data(query_conditions, collection)
        if res is not None:
            try:
                result = self.use_collection(collection).update_one(query_conditions, {"$set": after_change})
                return result.modified_count
            except Exception as e:
                logs.error(f"更新数据失败：{e}")
                raise
        else:
            logs.info("查询条件不存在")
            return 0

    def delete_collection(self, search, collection):
        if not isinstance(search, dict):
            raise TypeError("参数必须为dict类型")
        if not collection:
            raise ValueError("集合名不能为空")
        try:
            result = self.use_collection(collection).delete_one(search)
            return result.deleted_count
        except Exception as e:
            logs.error(f"删除单条数据失败：{e}")
            raise

    def delete_many_collection(self, search, collection):
        if not isinstance(search, dict):
            raise TypeError("参数必须为dict类型")
        if not collection:
            raise ValueError("集合名不能为空")
        try:
            result = self.use_collection(collection).delete_many(search)
            return result.deleted_count
        except Exception as e:
            logs.error(f"批量删除数据失败：{e}")
            raise

    def drop_collection(self, collection):
        if not collection:
            raise ValueError("集合名不能为空")
        try:
            self.use_collection(collection).drop()
            logs.info("delete success")
            return True
        except Exception as e:
            logs.error(f"删除集合失败：{e}")
            raise

class ConnectSSH(object):
    def __init__(self, host=None, port=22, username=None, password=None, timeout=None):
        self.__conn_info = {
            'hostname': conf.get_section_ssh('host') if host is None else host,
            'port': int(conf.get_section_ssh('port')) if host is None else int(port),
            'username': conf.get_section_ssh('username') if username is None else username,
            'password': conf.get_section_ssh('password') if password is None else password,
            'timeout': int(conf.get_section_ssh('timeout')) if timeout is None else int(timeout)
        }

        try:
            self.__client = paramiko.SSHClient()
            self.__client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.__client.connect(**self.__conn_info)

            if self.__client:
                logs.info('{}服务端连接成功'.format(self.__conn_info['hostname']))
        except Exception as e:
            logs.error(f"连接SSH失败：{str(traceback.format_exc())}")
            raise

    def close(self):
        try:
            if hasattr(self, '_ConnectSSH__client') and self.__client:
                self.__client.close()
            return True
        except Exception as e:
            logs.error(f"关闭SSH连接失败：{e}")
            return False

    def get_ssh_content(self, command=None):
        if not command:
            command = conf.get_section_ssh('command')
        if not command:
            raise ValueError("命令不能为空")
        
        try:
            stdin, stdout, stderr = self.__client.exec_command(command)
            content = stdout.read().decode()
            error = stderr.read().decode()
            if error:
                logs.error(f"执行命令错误：{error}")
            return content
        except Exception as e:
            logs.error(f"执行命令失败：{str(traceback.format_exc())}")
            raise

