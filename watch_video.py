import time
import requests
import re
import json

from config import uv_id
from main import headers


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
        print("《%s》已经学习完毕，跳过" % video_name)
        return 1
    else:
        print("《%s》尚未学习，现在开始自动学习" % video_name)
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
            print('错误')
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
