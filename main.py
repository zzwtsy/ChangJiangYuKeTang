# -*- coding: utf-8 -*-
# version 4
# developed by zk chen

import requests
import re
import json

import build_requests
from config import headers

course_id = []
chapter_map = {}

if __name__ == "__main__":
    # csrftoken = input("请输入csrftoken：")
    # sessionid = input("请输入sessionid：")
    # 获取userid
    response = requests.get('https://changjiang.yuketang.cn/v2/api/web/userinfo', headers=headers).text
    user_id = re.search(r'"user_id":(.*?),', response)
    user_id = user_id
    response = requests.get('https://changjiang.yuketang.cn/v2/api/web/courses/list?identity=2',
                            headers=headers).json()
    if response['errmsg'] != 'Success':
        print("csrftoken或者sessionid有问题请检查！")
        exit(1)
    index = 0
    # 获取课程id 和 课程名字
    for res2 in response['data']['list']:
        course_id.append(res2['classroom_id'])
        print("编号：" + str(index + 1) + " 课名：" + str(res2["course"]['name']))
        index += 1
    number = int(input("你想刷哪门课呢？请输入编号："))
    cid = str(course_id[number - 1])
    url = 'https://changjiang.yuketang.cn/v2/api/web/logs/learn/%s?actype=-1&page=0&offset=20&sort=-1' % cid
    response = requests.get(url, headers=headers).json()
    if response['data']['prev_id'] == -1:
        print('该课程尚无内容！程序推出....')
        exit(1)
    if response['errcode'] != 0:
        print(response)
        exit(1)
    courseware_id = []
    for res1 in response['data']['activities']:
        if res1['type'] != 15:
            continue
        else:
            courseware_id.append(res1['courseware_id'])
            chapter_map[res1['courseware_id']] = res1['title']
        data = {
            'cid': cid,
            'new_id': courseware_id
        }

        headers['classroom-id'] = cid
        headers['xtbz'] = 'ykt'
        headers['Referer'] = 'https://changjiang.yuketang.cn/v2/web/studentLog/%s' % cid
        response = requests.post('https://changjiang.yuketang.cn/mooc-api/v1/lms/learn/course/pub_new_pro',
                                 headers=headers, data=json.dumps(data)).json()
        for res2 in response['data']:
            url = 'https://changjiang.yuketang.cn/c27/online_courseware/xty/kls/pub_news/%s/' % res2
            ret = requests.get(url, headers=headers).json()
            if ret['success'] == 'False':
                print('获取课程数据时发生错误: ' + ret)
                exit(1)
            temp1 = 0
            for s in ret['data']['content_info']:
                if 'leaf_list' not in s:
                    continue
                if s['leaf_list']:
                    temp1 += 1
                    for classInfo in s['leaf_list']:
                        if classInfo['leaf_type'] != 0:
                            print('《%s》非视频,跳过' % classInfo['title'])
                            continue
                        VideoId = classInfo['id']
                        build_requests.get_class_info_dict(cid, VideoId, classInfo['title'])
                if s['section_list']:
                    for k in s['section_list']:
                        if len(k['leaf_list']) == 1:
                            for classInfo in k['leaf_list']:
                                if classInfo['leaf_type'] != 0:
                                    print('《%s》非视频,跳过' % classInfo['title'])
                                    continue
                                VideoId = classInfo['id']
                                build_requests.get_class_info_dict(cid, VideoId, classInfo['title'])
                        else:
                            temp2 = 0
                            while temp2 < len(k['leaf_list']):
                                classInfo = k['leaf_list'][temp2]
                                temp2 += 1
                                if classInfo['leaf_type'] != 0:
                                    print('《%s》非视频,跳过' % classInfo['title'])
                                    continue
                                VideoId = classInfo['id']
                                build_requests.get_class_info_dict(cid, VideoId, classInfo['title'])
                print("^^^《%s》已完成^^^" % s['name'])
