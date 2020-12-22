#!/root/.pyenv/shims/python3
# -*- encoding: utf-8 -*-
# requires a recent enough python with idna support in socket
# pyopenssl, cryptography and idna
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

#定义发送钉钉告警的函数
def send_to_ding(access_token,content):
    header = {
        "Content-Type": "application/json",
        "charset": "utf-8"
        }
    data = {
         "msgtype": "text",
            "text": {
                "content": content
            },
		"at":{
         #这里填写你要@的人的电话
	    "atMobiles":['电话'],
	    "isAtALL":False
	}
        }
    sendData = json.dumps(data)
    request = urllib.request.Request(access_token,data = sendData.encode(encoding='UTF8'),headers = header)
    urlopen = urllib.request.urlopen(request)
    print(urlopen.read())
#钉钉机器人的链接
access_token="httpsXXXXXXXXXXXXXXXXXXXXXXXXXX"

HostInfo = namedtuple(field_names='cert hostname peername', typename='HostInfo')

#要监控的地址，可以填写多个
HOSTS = [
    ('www.baidu.com', 443),
    ('www.taobao.com', 443)
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
    text='以下H5页面SSL证书有效天数数量小于600天，请及时更换：' \
         '%s' % (s)
    #对天数进行半段，并执行钉钉告警函数
    if count_days < 600:
        send_to_ding(access_token,text)

def check_it_out(hostname, port):
    hostinfo = get_certificate(hostname, port)
    print_basic_info(hostinfo)


import concurrent.futures
if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:
        for hostinfo in e.map(lambda x: get_certificate(x[0], x[1]), HOSTS):
            print_basic_info(hostinfo)
