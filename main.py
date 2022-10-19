# -*- coding: utf-8 -*-
# version 4
# developed by zk chen
import time

import requests
import re
import json

from config import headers, select, uv_id

课程id = []
章节map = {}


def one_video_watcher(video_id, video_name, cid, user_id, classroomid, skuid):
    video_id = str(video_id)
    classroomid = str(classroomid)
    url = "https://changjiang.yuketang.cn/video-log/heartbeat/"
    get_url = "https://changjiang.yuketang.cn/video-log/get_video_watch_progress/?cid=" + str(
        cid) + "&user_id=" + user_id + "&classroom_id=" + classroomid + "&video_type=video&vtype=rate&video_id=" + str(
        video_id) + "&snapshot=1&term=latest&uv_id=" + uv_id
    progress = requests.get(url=get_url, headers=headers)
    if_completed = '0'
    try:
        if_completed = re.search(r'"completed":(.+?),', progress.text).group(1)
    except:
        pass
    if if_completed == '1':
        print(video_name + "已经学习完毕，跳过")
        return 1
    else:
        print(video_name + "，尚未学习，现在开始自动学习")
    video_frame = 0
    val = 0
    learning_rate = 20
    t = time.time()
    timestap = int(round(t * 1000))
    while val != "1.0" and val != '1':
        heart_data = []
        for i in range(50):
            heart_data.append(
                {
                    "i": 5,
                    "et": "loadeddata",
                    "p": "web",
                    "n": "ws",
                    "lob": "cloud4",
                    "cp": video_frame,
                    "fp": 0,
                    "tp": 0,
                    "sp": 1,
                    "ts": str(timestap),
                    "u": int(user_id),
                    "uip": "",
                    "c": cid,
                    "v": int(video_id),
                    "skuid": skuid,
                    "classroomid": classroomid,
                    "cc": video_id,
                    "d": 4976.5,
                    "pg": "4512143_tkqx",
                    "sq": 2,
                    "t": "video"
                }
            )
            video_frame += learning_rate
            max_time = int((time.time() + 3600) * 1000)
            timestap = min(max_time, timestap + 1000 * 15)
        data = {"heart_data": heart_data}
        r = requests.post(url=url, headers=headers, json=data)
        # print(r.text)
        try:
            error_msg = json.loads(r.text)["message"]
            if "anomaly" in error_msg:
                video_frame = 0
        except:
            pass
        try:
            delay_time = re.search(r'Expected available in(.+?)second.', r.text).group(1).strip()
            print("由于网络阻塞，万恶的雨课堂，要阻塞" + str(delay_time) + "秒")
            time.sleep(float(delay_time) + 0.5)
            video_frame = 0
            print("恢复工作啦～～")
            submit_url = "https://changjiang.yuketang.cn/mooc-api/v1/lms/exercise/problem_apply/?term=latest&uv_id=" + uv_id
            r = requests.post(url=submit_url, headers=headers, data=data)
        except:
            pass
        progress = requests.get(url=get_url, headers=headers)
        tmp_rate = re.search(r'"rate":(.+?)[,}]', progress.text)
        if tmp_rate is None:
            return 0
        val = tmp_rate.group(1)
        print("学习进度为：" + str(float(val) * 100) + "%/100%" + " last_point: " + str(video_frame))
        time.sleep(0.7)
    print("视频" + video_id + " " + video_name + "学习完成！")
    return 1


if __name__ == "__main__":
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
    for i in response['data']['list']:
        课程id.append(i['classroom_id'])
        print("编号：" + str(index + 1) + " 课名：" + str(i["course"]['name']))
        index += 1
    number = int(input("你想刷哪门课呢？请输入编号：\n"))
    cid = str(课程id[number - 1])
    url = 'https://changjiang.yuketang.cn/v2/api/web/logs/learn/%s?actype=-1&page=0&offset=20&sort=-1' % cid
    response = requests.get(url, headers=headers).json()
    if response['data']['prev_id'] == -1:
        print('该课程尚无内容！程序推出....')
        exit(1)
    if response['errcode'] != 0:
        print(response)
        exit(1)
    courseware_id_tmp = []
    for i in response['data']['activities']:
        courseware_id_tmp.append(i['courseware_id'])
        章节map[i['courseware_id']] = i['title']
    courseware_id = []
    n = 1
    while n <= 2:
        courseware_id.append(courseware_id_tmp[n])
        n += 1
    data = {
        'cid': cid,
        'new_id': courseware_id
    }

    headers['classroom-id'] = cid
    headers['xtbz'] = 'ykt'
    headers['Referer'] = 'https://changjiang.yuketang.cn/v2/web/studentLog/%s' % cid
    if select:
        skuid = requests.get(url='https://changjiang.yuketang.cn/v2/api/web/classrooms/%s?role=5' % cid,
                             headers=headers).json()['data']['free_sku_id']
        get_url = 'https://changjiang.yuketang.cn/c27/online_courseware/schedule/score_detail/single/%s/0/' % skuid
        ret = requests.get(url=get_url, headers=headers).json()
        for i in ret['data']['leaf_level_infos']:
            if i['leaf_level_title'] != 'Video':
                continue
            get_url = 'https://changjiang.yuketang.cn/mooc-api/v1/lms/learn/leaf_info/%s/%s/' % (cid, i['id'])
            getccid = requests.get(url=get_url, headers=headers).json()
            skuid = getccid['data']['sku_id']
            user_id = getccid['data']['user_id']
            ccid = getccid['data']['content_info']['media']['ccid']
            course_id = getccid['data']['course_id']
            one_video_watcher(i['id'], i['leaf_chapter_title'], course_id, str(user_id), cid, skuid)
        print("---------------------------已完成-------------------------------")
    else:
        response = requests.post('https://changjiang.yuketang.cn/mooc-api/v1/lms/learn/course/pub_new_pro',
                                 headers=headers, data=json.dumps(data)).json()
        for i in response['data']:
            temp = 章节map[i]
            if '期末考试' in temp:
                print("%s，跳过...." % 章节map[i])
                continue
            if '开课通知' in temp:
                print("%s，跳过...." % 章节map[i])
                continue
            if response['data'][i]['total_done'] == 1:
                print("%s已完成，跳过...." % 章节map[i])
                continue
            url = 'https://changjiang.yuketang.cn/c27/online_courseware/xty/kls/pub_news/%s/' % i
            ret = requests.get(url, headers=headers).json()
            m = 0
            temp1 = 0
            for s in ret['data']['content_info']:
                if s['leaf_list'] and s['leaf_list'][temp1]['leaf_type'] != 6:
                    temp1 += 1
                    for classInfo in s['leaf_list']:
                        if classInfo['leaf_type'] == 6:
                            print('非视频,跳过')
                            continue
                        VideoId = classInfo['id']
                        get_url = 'https://changjiang.yuketang.cn/mooc-api/v1/lms/learn/leaf_info/%s/%s/' % (
                            cid, VideoId)
                        getccid = requests.get(url=get_url, headers=headers).json()
                        skuid = getccid['data']['sku_id']
                        user_id = getccid['data']['user_id']
                        ccid = getccid['data']['content_info']['media']['ccid']
                        course_id = getccid['data']['course_id']
                        one_video_watcher(VideoId, s['name'], course_id, str(user_id), cid, skuid)
                        print("%s已完成...." % 章节map[i])
                else:
                    if s['section_list']:
                        for k in s['section_list']:
                            m += 1
                            if len(k['leaf_list']) == 1:
                                for classInfo in k['leaf_list']:
                                    if classInfo['leaf_type'] == 6:
                                        print('非视频,跳过')
                                        continue
                                    VideoId = classInfo['id']
                                    get_url = 'https://changjiang.yuketang.cn/mooc-api/v1/lms/learn/leaf_info/%s/%s/' % (
                                        cid, VideoId)
                                    getccid = requests.get(url=get_url, headers=headers).json()
                                    skuid = getccid['data']['sku_id']
                                    user_id = getccid['data']['user_id']
                                    ccid = getccid['data']['content_info']['media']['ccid']
                                    course_id = getccid['data']['course_id']
                                    one_video_watcher(VideoId, s['name'], course_id, str(user_id), cid, skuid)
                                    print("%s已完成...." % 章节map[i])
                            else:
                                temp2 = 0
                                while temp2 < len(k['leaf_list']):
                                    classInfo = k['leaf_list'][temp2]
                                    temp2 += 1
                                    if classInfo['leaf_type'] == 6:
                                        print('非视频,跳过')
                                        continue
                                    VideoId = classInfo['id']
                                    get_url = 'https://changjiang.yuketang.cn/mooc-api/v1/lms/learn/leaf_info/%s/%s/' % (
                                        cid, VideoId)
                                    getccid = requests.get(url=get_url, headers=headers).json()
                                    skuid = getccid['data']['sku_id']
                                    user_id = getccid['data']['user_id']
                                    ccid = getccid['data']['content_info']['media']['ccid']
                                    course_id = getccid['data']['course_id']
                                    one_video_watcher(VideoId, s['name'], course_id, str(user_id), cid, skuid)
                                    print("%s已完成...." % 章节map[i])
