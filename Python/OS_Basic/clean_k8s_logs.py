#!/usr/bin/python3
# os.path.getatime(file)   ：输出最近访问时间1318921018.0
# os.path.getctime(file)   ：输出文件创建时间
# os.path.getmtime(file)   ：输出最近修改时间
# os.listdir(dirname)：列出dirname下的目录和文件
# os.path.isdir(name):判断name是不是一个目录，name不是目录就返回false
# os.path.isfile(name):判断name是不是一个文件，不存在name也返回false
# os.path.join(path,name):连接目录与文件名或目录
# os.remove(dir) #dir为要删除的文件夹或者文件路径
# os.rmdir(path) #path要删除的目录的路径。需要说明的是，使用os.rmdir删除的目录必须为空目录，否则函数出错。

import os
from datetime import datetime,timedelta

shijiancha = timedelta(days=1) #设置需要清理的时间
dir = os.path.join('/yc/data/kubernetes/logs')
#print(dirs)

def clear_file(dir):
    # 获取目录下的文件和文件夹
    dirs = os.listdir(dir)
    #遍历目录下的文件
    for d in dirs:
   # 拼接到当前目录
       f = os.path.join(dir,d)
       #判断是否是文件
       if os.path.isfile(f):
           #os.path.getmtime获取文件的创建时间戳，在转换成日期
           s = datetime.fromtimestamp(os.path.getctime(f))
            #判断文件是否是满足删除条件
           if ( datetime.now()-s )>shijiancha:
                     os.remove(f)
                     print(f,'删除')
       #若不是文件，那就是文件夹（目录），使用递归，继续以上操作
       else:
           clear_file(f)

clear_file(dir)
