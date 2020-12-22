#!/root/.virtualenvs/wechat/bin/python
# usage: send message via wechat
import datetime
#获取系统当前时间
Startime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
from OpenSSL import SSL
from cryptography import x509
from cryptography.x509.oid import NameOID
import idna
import time
import json
import urllib
import requests
from socket import socket
from collections import namedtuple
import smtplib
from email.mime.text import MIMEText
import requests, sys, json
import urllib3
urllib3.disable_warnings()

# ------------------------------ 微信相关配置 ---------------------
###填写参数###
# Corpid是企业号的标识
Corpid = "ww6e4cd89fc72c500a1"
# Secret是管理组凭证密钥
Secret = "0N1I9G6o6bvIwA-Ig0AuDMo7JP1BYb7tSOCc5G-r8-s1"
# 应用ID
Agentid = "1000002"
# token_config文件放置路径
Token_config = r'/tmp/zabbix_wechat_config.json'


def GetTokenFromServer(Corpid, Secret):
    """获取access_token"""
    Url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    Data = {
        "corpid": Corpid,
        "corpsecret": Secret
    }
    r = requests.get(url=Url, params=Data, verify=False)
    print(r.json())
    if r.json()['errcode'] != 0:
        return False
    else:
        Token = r.json()['access_token']
        file = open(Token_config, 'w')
        file.write(r.text)
        file.close()
        return Token


def SendMessage(Partyid, Subject, Content):
    """发送消息"""
    # 获取token信息
    try:
        file = open(Token_config, 'r')
        Token = json.load(file)['access_token']
        file.close()
    except:
        Token = GetTokenFromServer(Corpid, Secret)

    # 发送消息
    Url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s" % Token
    Data = {
        "toparty": Partyid,
        "msgtype": "text",
        "agentid": Agentid,
        "text": {"content": Subject + '\n' + Content},
        "safe": "0"
    }
    r = requests.post(url=Url, data=json.dumps(Data), verify=False)

    # 如果发送失败，将重试三次
    n = 1
    while r.json()['errcode'] != 0 and n < 4:
        n = n + 1
        Token = GetTokenFromServer(Corpid, Secret)
        if Token:
            Url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s" % Token
            r = requests.post(url=Url, data=json.dumps(Data), verify=False)
            print(r.json())

    return r.json()

# --------------------------------- 证书相关配置 ----------------------------
HostInfo = namedtuple(field_names='cert hostname peername', typename='HostInfo')

#要监控的地址，可以填写多个
HOSTS = [
    # ('worktile.com', 443),
    # ('pingcode.com', 443),
    # ('at.worktile.com', 443),
    # ('at.pingcode.com', 443),
    # ('pingcode.site', 443),
    # ('web-bet.pingcode.site', 443),
    # ('harbor.pingcode.live', 443),
    ('k8s.pingcode.live', 443),
]

#获取证书信息
def verify_cert(cert, hostname):
    # verify notAfter/notBefore, CA trusted, servername/sni/hostname
    cert.has_expired()
    # service_identity.pyopenssl.verify_hostname(client_ssl, hostname)
    # issuer

def get_certificate(hostname, port):
    hostname_idna = idna.encode(hostname)
    sock = socket()

    sock.connect((hostname, port))
    peername = sock.getpeername()
    ctx = SSL.Context(SSL.SSLv23_METHOD) # most compatible
    ctx.check_hostname = False
    ctx.verify_mode = SSL.VERIFY_NONE

    sock_ssl = SSL.Connection(ctx, sock)
    sock_ssl.set_connect_state()
    sock_ssl.set_tlsext_host_name(hostname_idna)
    sock_ssl.do_handshake()
    cert = sock_ssl.get_peer_certificate()
    crypto_cert = cert.to_cryptography()
    sock_ssl.close()
    sock.close()
    return HostInfo(cert=crypto_cert, peername=peername, hostname=hostname)


def print_basic_info(hostinfo):
    #计算证书剩余的天数
    start = time.mktime(time.strptime(str(Startime), '%Y-%m-%d %H:%M:%S'))
    end = time.mktime(time.strptime(str(hostinfo.cert.not_valid_after), '%Y-%m-%d %H:%M:%S'))
    count_days = int((end - start) / (24 * 60 * 60))

    s = '''{hostname}
    \t起始时间: {startime}
    \t到期时间:  {endtime}
    \t剩余过期天数：{count}
    '''.format(
            hostname=hostinfo.hostname,
            # peername=hostinfo.peername,
            # commonname=get_common_name(hostinfo.cert),
            # SAN=get_alt_names(hostinfo.cert),
            # issuer=get_issuer(hostinfo.cert),
            startime=hostinfo.cert.not_valid_before,
            endtime=hostinfo.cert.not_valid_after,
            count=count_days
    )
    print(s)
    text='SSL证书有效天数数量小于60天，请及时更换：' \
         '%s' % (s)
    #对天数进行半段，并执行钉钉告警函数
    if count_days < 60:
    #     send_to_ding(access_token,text)
        Partyid = '1'
        Subject = str("SSL证书信息通知:")
        Status = SendMessage(Partyid, Subject, Content=text)


# if __name__ == '__main__':
    # Partyid = str(sys.argv[1])
    # Subject = str(sys.argv[2])
    # Content = str(sys.argv[3])
    # % python weixin.py 1 test test
    # Partyid = '1'

    # Subject = str("SSL证书信息通知:")
    # Content = str("xxxx")

    # Status = SendMessage(Partyid, Subject, Content)
    # print(Status)

import concurrent.futures
if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:
        for hostinfo in e.map(lambda x: get_certificate(x[0], x[1]), HOSTS):
            print_basic_info(hostinfo)

