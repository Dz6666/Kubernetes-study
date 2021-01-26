import OpenSSL
from OpenSSL import crypto
from cryptography import x509
import time, datetime
from dateutil import parser
import idna
from socket import socket
from collections import namedtuple
import requests, sys, json, subprocess
import urllib3, urllib
urllib3.disable_warnings()

# ------------------------------ 微信相关配置 ---------------------
Corpid = "ww6e4cd89fc72c500a"
Secret = "0N1I9G6o6bvIwA-Ig0AuDMo7JP1BYb7tSOCc5G-r8-s"
# 应用ID
Agentid = "1000002"
Token_config = r'/tmp/ssl_wechat_config.json'


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

    n = 1
    while r.json()['errcode'] != 0 and n < 4:
        n = n + 1
        Token = GetTokenFromServer(Corpid, Secret)
        if Token:
            Url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s" % Token
            r = requests.post(url=Url, data=json.dumps(Data), verify=False)
            # print(r.json())
    return r.json()

# ------------------- 证书相关配置 ----------------------
def k8s_cert(cert_file):
    
    cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, open(cert_file).read())
    certIssue = cert.get_issuer()

    # print ("证书版本:            ",cert.get_version() + 1)
    # print ("证书序列号:          ",hex(cert.get_serial_number()))
    # print ("证书中使用的签名算法: ",cert.get_signature_algorithm().decode("UTF-8"))
    # print ("颁发者:              ",certIssue.commonName)
    

    #获取系统当前时间
    Timenow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("当前系统时间 {}".format(Timenow))
    start = time.mktime(time.strptime(str(Timenow), '%Y-%m-%d %H:%M:%S'))

    # 签署时间
    # Startime = parser.parse(cert.get_notBefore().decode("UTF-8"))
    # Startime_str = Startime.strftime('%Y-%m-%d %H:%M:%S')
    # print(Startime_str)
    # print("有效期从:             ",Startime.strftime('%Y-%m-%d %H:%M:%S'))

    # 到期时间
    Endtime = parser.parse(cert.get_notAfter().decode("UTF-8"))
    Endtime_str = Endtime.strftime('%Y-%m-%d %H:%M:%S')
    end = time.mktime(time.strptime(str(Endtime_str), '%Y-%m-%d %H:%M:%S'))
    print("证书到期时间 {}".format(Endtime_str))
    # print ("到:                   ",Endtime.strftime('%Y-%m-%d %H:%M:%S'))

    count_days = int((end - start) / (24 * 60 * 60))
    print(count_days)

    # print(tart)
    # end = time.mktime(time.strptime(str(hostinfo.cert.not_valid_after), '%Y-%m-%d %H:%M:%S'))
    # count_days = int((end - start) / (24 * 60 * 60))
    # print(count_days)


    # print("证书是否已经过期:      ",cert.has_expired())
    # print("公钥长度" ,cert.get_pubkey().bits())
    # print("公钥:\n" ,OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, cert.get_pubkey()).decode("utf-8"))
    # print("主体信息:")
    # print("CN : 通用名称  OU : 机构单元名称")
    # print("O  : 机构名    L  : 地理位置")
    # print("S  : 州/省名   C  : 国名")

    # for item in certIssue.get_components():
    #     print(item[0].decode("utf-8"), "  ——  ",item[1].decode("utf-8"))
    # print(cert.get_extension_count())

    s = '''\t到期时间:  {Endtime_str}
    \t剩余过期天数：{count}
    '''.format(
            Endtime_str=Endtime_str,
            count=count_days
    )

    text='北京集群K8S证书有效天数数量小于30天，请及时更换：' \
         '%s' % (s)
    if count_days < 30:
        Partyid = '1'
        #Partyid = '1000002'
        Subject = str("")
        # Status = SendMessage(Partyid, Subject, Content=text)

if __name__ == '__main__':
    k8s_cert(cert_file = '/root/Kubernetes-study/66_Kubernetes-工作实践总结/k8s证书检测/apiserver_xianshang.crt')

