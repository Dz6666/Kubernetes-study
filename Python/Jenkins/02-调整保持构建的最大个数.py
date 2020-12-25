import sys
import jenkins
import xml.etree.ElementTree as ET
import re
import logging

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
        # result = re.search('CD', job_name)

        # 测试Job
        # test_name1 = 'standard_job_CD'
        # test_name2 = 'non-standard_job_CD'

        # if result:
            # print(job_name)
            # list.append(job_name)
        # print(list)
        # if job_name == "non-standard_job_CD":
        if job_name:
            jobs_config = server.get_job_config(job_name)
            print(jobs_config)

            # 检查是否开启丢弃旧的构建
            if 'jenkins.model.BuildDiscarderProperty' in jobs_config:
                print('BuildDiscarderProperty configured')
                continue

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

    # 在properties标签后面添加新标签
    for properties in root.iter('properties'):
        BuildDiscarderProperty = ET.SubElement(properties, 'jenkins.model.BuildDiscarderProperty')
        strategy = ET.SubElement(BuildDiscarderProperty, 'strategy', attrib={'class': 'hudson.tasks.LogRotator'})
        daysToKeep = ET.SubElement(strategy, 'daysToKeep')
        daysToKeep.text = '1'
        numToKeep = ET.SubElement(strategy, 'numToKeep')
        numToKeep.text = '20'
        artifactDaysToKeep = ET.SubElement(strategy, 'artifactDaysToKeep')
        artifactDaysToKeep.text = '-1'
        artifactNumToKeep = ET.SubElement(strategy, 'artifactNumToKeep')
        artifactNumToKeep.text = '-1'

    # 美化xml格式
    prettyXml(root, '    ', '\n')
    tree.write(tmp_xml)

def prettyXml(element, indent, newline, level = 0): # elemnt为传进来的Elment类，参数indent用于缩进，newline用于换行
    if element:  # 判断element是否有子元素
        if element.text == None or element.text.isspace(): # 如果element的text没有内容
            element.text = newline + indent * (level + 1)
        else:
            element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * (level + 1)

    temp = list(element) # 将elemnt转成list
    for subelement in temp:
        if temp.index(subelement) < (len(temp) - 1):
            subelement.tail = newline + indent * (level + 1)
        else:
            subelement.tail = newline + indent * level
        prettyXml(subelement, indent, newline, level = level + 1)

if __name__ == '__main__':
    username = 'xxxxxxxx'
    password = 'xxxxxxxxxxxxxx'
    add_config_job(username, password)
