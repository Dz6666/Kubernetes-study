#此脚本用于更新 Git 浅克隆 & 克隆深度
import sys
import jenkins
import xml.etree.ElementTree as ET
import re
import logging

logging.basicConfig(level=logging.DEBUG,
          format='%(asctime)s %(filename)s %(levelname)s %(message)s',
          datefmt='%a, %d %b %Y %H:%M:%S',
          filename='/tmp/alpha_jenkins.log',
          filemode='w')

# def modify_xml(tmp_xml):
#     tree = ET.parse(tmp_xml)
#     root = tree.getroot()
#
#     for shallow in root.iter('shallow'):
#         shallow.text = 'true'
#     for depth in root.iter('depth'):
#         depth.text = '1'
#
#     tree.write(tmp_xml)

def add_config_job(username, password):
    # server获取信息
    server = jenkins.Jenkins('http://jenkins.pingcode.live', username=username, password=password)
    view_info = server.get_info()
    print(view_info)
    count = 0
    list = []
    #依次获取对应视图里面的jobs名称及配置信息
    for num in range(0,len(view_info['jobs'])):
        job_name = view_info['jobs'][num]['name']   # .endswitch("CD-job")
        # print(job_name)
        result = re.search('CD', job_name)

        # 测试Job
        # test_name1 = 'standard_job_CD'
        # test_name2 = 'non-standard_job_CD'

        if result:
            # print(job_name)
            # list.append(job_name)
    # print(list)
        # if job_name == "non-standard_job_CD":
            jobs_config = server.get_job_config(job_name)
            print(jobs_config)

            # 检查是否开启浅拷贝
            if '<shallow>true</shallow>' not in jobs_config:
                print(job_name + "shallow is not true")
                if '<depth>1</depth>' not in jobs_config:
                    logging.info('{} --- depth is not set...'.format(job_name))
            else:
                    logging.info('{} --- shallow is true and depth is  set 1...'.format(job_name))

            # 将配置写入xml文件中
            tmp_xml = '/tmp/job_config.xml'
            with open(tmp_xml, 'w') as f:
                f.write(jobs_config)
                f.write('\n')

            try:
                # 更新第一次
                modify_xml1(tmp_xml)
            #     # 配置xml文件，添加对应的标签
            #     # modify_xml(tmp_xml)
                with open(tmp_xml, 'r') as f:
                    jobs_config_new = f.read()
            #       # 此处的server用于修改配置，配置的名称在上面定义好
                    server = jenkins.Jenkins('http://jenkins.pingcode.live', username=username, password=password)

            #       job_name_new = 'new/' + job_name
            #       # print(job_name_new)
            #       # print(jobs_config_new)
            #       # 修改job配置前需要先对其执行disable操作
                    server.disable_job(job_name)
                    server.reconfig_job(job_name, jobs_config_new)

                    server.enable_job(job_name)

                # 更新第二次
                modify_xml2(tmp_xml)
                with open(tmp_xml, 'r') as f:
                    jobs_config_new = f.read()
                    #       # 此处的server用于修改配置，配置的名称在上面定义好
                    server = jenkins.Jenkins('http://jenkins.pingcode.live', username=username,
                                             password=password)

                      # job_name_new = 'new/' + job_name
                      # print(job_name_new)
                      # print(jobs_config_new)
                      # 修改job配置前需要先对其执行disable操作
                    server.disable_job(job_name)
                    server.reconfig_job(job_name, jobs_config_new)

                    server.enable_job(job_name)

            except Exception as e:
                # print(e)
                # 将配置失败的job名称保存到/tmp/config_failed.list列表中
                fail_list = '/tmp/config_failed.list'
                if count == 0:
                    with open(fail_list, 'w') as f:
                        f.write(job_name + '\n')
                else:
                    with open(fail_list, 'a') as f:
                        f.write(job_name + '\n')
                        count = count + 1

def modify_xml1(tmp_xml):
    tree = ET.parse(tmp_xml)
    root = tree.getroot()

    # 更新选项
    for shallow in root.iter('shallow'):
        shallow.text = 'true'
        print('shallow is true........')
    # for properties in root.iter('properties'):
    #     BuildDiscarderProperty = ET.SubElement(properties,

    tree.write(tmp_xml)

def modify_xml2(tmp_xml):
    tree = ET.parse(tmp_xml)
    root = tree.getroot()
    # 深浅需要另行添加
    for depth in root.text('depth'):
        depth.text = '1'
    tree.write(tmp_xml)

if __name__ == '__main__':
    username = 'xxxx'
    password = 'xxxxxxxxxxxx'
    add_config_job(username, password)
