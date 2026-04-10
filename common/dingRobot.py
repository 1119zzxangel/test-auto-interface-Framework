import urllib.parse                # 导入URL编码模块
import requests                    # 导入HTTP请求库
import time                        # 导入时间模块
import hmac                        # 导入HMAC加密算法
import hashlib                     # 导入哈希算法库
import base64                      # 导入Base64编码模块

def generate_sign():
    """
    签名计算
    把timestamp+"\n"+密钥当做签名字符串，使用HmacSHA256算法计算签名，然后进行Base64 encode，
    最后再把签名参数再进行urlEncode，得到最终的签名（需要使用UTF-8字符集）
    :return: 返回当前时间戳、加密后的签名
    """
    timestamp = str(round(time.time() * 1000))  # 获取当前时间戳（毫秒级）并转字符串
    secret = '123'                               # 定义钉钉机器人加签密钥
    secret_enc = secret.encode('utf-8')          # 密钥转UTF-8字节
    str_to_sign = '{}\n{}'.format(timestamp, secret)  # 拼接待签名字符串
    str_to_sign_enc = str_to_sign.encode('utf-8')    # 待签名字符串转字节
    hmac_code = hmac.new(secret_enc, str_to_sign_enc, digestmod=hashlib.sha256).digest()  # HmacSHA256加密
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))  # Base64编码后URL编码
    return timestamp, sign                        # 返回时间戳和签名

def send_dd_msg(content_str, at_all=True):
    """
    向钉钉机器人推送结果
    :param content_str: 发送的内容
    :param at_all: @全员，默认为True
    :return:
    """
    timestamp_and_sign = generate_sign()          # 调用方法获取时间戳与签名
    url = f'https://oapi.dingtalk.com/robot/send?access_token=75d6628cefedc8225695dcde2577f03336f0099cd16d93988a68ad243cf9dd6f&timestamp={timestamp_and_sign[0]}&sign={timestamp_and_sign[1]}'  # 拼接钉钉请求URL
    headers = {'Content-Type': 'application/json;charset=utf-8'}  # 设置请求头
    data = {                                      # 构造消息体
        "msgtype": "text",                        # 消息类型为文本
        "text": {                                 # 文本内容
            "content": content_str
        },
        "at": {                                    # @配置
            "isAtAll": at_all
        },
    }
    res = requests.post(url, json=data, headers=headers)  # 发送POST请求
    return res.text                              # 返回响应结果