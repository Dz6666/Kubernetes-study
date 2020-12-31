from urllib.request import urlopen
from http.client import HTTPResponse
 
# 打开一个url返回一个响应对象，类文件对象
# 下面的连接访问后会有跳转
 
url = 'http://www.bing.com'
response:HTTPResponse = urlopen(url)    # GET 方法    # print(response, type(response).mro())
print(response.closed)                  # False
 
# HTTPResponse 提供上下文__enter__、__exit__，使用with语法
with response:
    print(1, type(response))    # http.client.HTTPResponse 类对象对象
    print(2, response.status, response.reason)  # 状态    200 OK
    print(3, response.geturl()) # 返回真正的URL  http://cn.bing.com/
    print(4, response.info())   # headers 响应头
    print(5, response.headers)  # headers 响应头
    print(6, response.read())   # 读取返回的内容
print(response.closed)          # True，上下文已关闭

