# -*- coding: utf-8 -*-
# 长江雨课堂自动刷课脚本
# version 4
# developed by zk chen

import time
import requests
import re
import json
import logging
import colorama
from typing import Dict, List

# 初始化日志配置
colorama.init(autoreset=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class YuKeTangAutomation:
    def __init__(self):
        # 初始化用户认证信息
        self.csrftoken = str(input("请输入csrftoken:"))
        self.sessionid = str(input("请输入sessionid:"))
        self.uv_id = input("请输入uv_id(随便输入好像也可以):")
        
        # 初始化请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/87.0.4280.67 Safari/537.36',
            'Content-Type': 'application/json',
            'Cookie': f'csrftoken={self.csrftoken}; sessionid={self.sessionid}; university_id={self.uv_id}; platform_id=3',
            'referer': 'https://changjiang.yuketang.cn/v2/web/index',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'university-id': self.uv_id,
            'uv-id': self.uv_id,
            'x-csrftoken': self.csrftoken,
            'xt-agent': 'web',
            'xtbz': 'cloud'
        }

        # 定义叶子节点类型
        self.leaf_type = {
            "video": 0,
            "homework": 6,
            "exam": 5,
            "recommend": 3,
            "discussion": 4
        }

    def watch_video(self, video_id: str, video_name: str, cid: str, user_id: str, classroomid: str, skuid: str) -> int:
        """观看单个视频

        Args:
            video_id: 视频ID
            video_name: 视频名称
            cid: 课程ID
            user_id: 用户ID
            classroomid: 教室ID
            skuid: SKU ID

        Returns:
            int: 1表示成功，0表示失败
        """
        # 获取视频观看进度的URL
        get_url = f"https://changjiang.yuketang.cn/video-log/get_video_watch_progress/?cid={cid}&user_id={user_id}&classroom_id={classroomid}&video_type=video&vtype=rate&video_id={video_id}&snapshot=1&term=latest&uv_id={self.uv_id}"
        progress = requests.get(url=get_url, headers=self.headers)

        # 检查视频是否已完成
        if_completed = '0'
        try:
            if_completed = re.search(r'"completed":(.+?),', progress.text).group(1)
        except:
            pass

        if if_completed == '1':
            logging.info(f"《{video_name}》已经学习完毕，跳过")
            return 1
        else:
            logging.info(f"《{video_name}》尚未学习，现在开始自动学习")

        # 视频观看进度相关参数
        video_frame = 0
        val = 0
        learning_rate = 20
        t = time.time()
        timestap = int(round(t * 1000))

        # 心跳请求URL
        url = "https://changjiang.yuketang.cn/video-log/heartbeat/"

        # 循环发送心跳请求直到视频完成
        while val != "1.0" and val != '1':
            heart_data = self._generate_heart_data(video_frame, timestap, user_id, cid, video_id, skuid, classroomid)
            data = {"heart_data": heart_data}
            
            # 发送心跳请求
            r = requests.post(url=url, headers=self.headers, json=data)
            
            # 处理异常情况
            try:
                error_msg = json.loads(r.text)["message"]
                if "anomaly" in error_msg:
                    video_frame = 0
            except:
                pass

            try:
                # 处理网络阻塞情况
                delay_time = re.search(r'Expected available in(.+?)second.', r.text).group(1).strip()
                logging.warning(f"由于网络阻塞，要阻塞{delay_time}秒")
                time.sleep(float(delay_time) + 0.5)
                video_frame = 0
                logging.info("恢复工作")
            except:
                pass

            # 获取当前进度
            progress = requests.get(url=get_url, headers=self.headers)
            tmp_rate = re.search(r'"rate":(.+?)[,}]', progress.text)
            if tmp_rate is None:
                return 0
            
            val = tmp_rate.group(1)
            logging.info(f"学习进度：{float(val) * 100:.1f}% (last_point: {video_frame})")
            
            # 更新参数
            video_frame += learning_rate
            max_time = int((time.time() + 3600) * 1000)
            timestap = min(max_time, timestap + 1000 * 15)
            time.sleep(0.7)

        logging.info(f"视频《{video_name}》(ID: {video_id}) 学习完成")
        return 1

    def _generate_heart_data(self, video_frame: int, timestap: int, user_id: str, cid: str, 
                            video_id: str, skuid: str, classroomid: str) -> List[Dict]:
        """生成心跳数据

        Args:
            video_frame: 视频帧
            timestap: 时间戳
            user_id: 用户ID
            cid: 课程ID
            video_id: 视频ID
            skuid: SKU ID
            classroomid: 教室ID

        Returns:
            List[Dict]: 心跳数据列表
        """
        heart_data = []
        learning_rate = 20
        for i in range(50):
            heart_data.append({
                "i": 5,
                "et": "loadeddata",
                "p": "web",
                "n": "ws",
                "lob": "cloud4",
                "cp": video_frame + i * learning_rate,
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
            })
        return heart_data

    def get_class_info(self, cid: str, video_id: str, name: str) -> None:
        """获取课程信息并观看视频

        Args:
            cid: 课程ID
            video_id: 视频ID
            name: 视频名称
        """
        get_url = f'https://changjiang.yuketang.cn/mooc-api/v1/lms/learn/leaf_info/{cid}/{video_id}/'
        response = requests.get(url=get_url, headers=self.headers).json()
        
        skuid = response['data']['sku_id']
        user_id = response['data']['user_id']
        course_id = response['data']['course_id']
        
        self.watch_video(video_id, name, course_id, str(user_id), cid, skuid)

    def process_course_content(self, content_info: List[Dict], cid: str) -> None:
        """处理课程内容

        Args:
            content_info: 课程内容信息
            cid: 课程ID
        """
        for section in content_info:
            if 'leaf_list' not in section:
                continue

            # 处理叶子节点列表
            if section['leaf_list']:
                for class_info in section['leaf_list']:
                    if class_info['leaf_type'] != 0:
                        logging.debug(f'《{class_info["title"]}》非视频，跳过')
                        continue
                    self.get_class_info(cid, class_info['id'], class_info['title'])

            # 处理小节列表
            if section['section_list']:
                for subsection in section['section_list']:
                    for class_info in subsection['leaf_list']:
                        if class_info['leaf_type'] != 0:
                            logging.debug(f'《{class_info["title"]}》非视频，跳过')
                            continue
                        self.get_class_info(cid, class_info['id'], class_info['title'])

            logging.info(f"章节《{section['name']}》已完成")

    def run(self) -> None:
        """运行自动刷课程序"""
        # 获取用户信息
        response = requests.get('https://changjiang.yuketang.cn/v2/api/web/userinfo', headers=self.headers).text

        # 获取课程列表
        response = requests.get('https://changjiang.yuketang.cn/v2/api/web/courses/list?identity=2',
                              headers=self.headers).json()
        
        if response['errmsg'] != 'Success':
            logging.error("认证失败：csrftoken或sessionid无效")
            return

        # 显示课程列表
        course_list = response['data']['list']
        for index, course in enumerate(course_list):
            print(f"编号：{index + 1} 课名：{course['course']['name']}")

        # 选择课程
        print("\n请选择要刷的课程编号：")
        number = int(input("请输入编号："))
        cid = str(course_list[number - 1]['classroom_id'])

        # 获取课程活动
        url = f'https://changjiang.yuketang.cn/v2/api/web/logs/learn/{cid}?actype=-1&page=0&offset=20&sort=-1'
        response = requests.get(url, headers=self.headers).json()

        if response['data']['prev_id'] == -1:
            logging.warning('该课程暂无内容，程序退出')
            return

        if response['errcode'] != 0:
            logging.error(f'获取课程活动失败：{response}')
            return

        # 处理课程活动
        courseware_ids = []
        chapter_map = {}
        
        for activity in response['data']['activities']:
            if activity['type'] != 15:
                continue
                
            courseware_ids.append(activity['courseware_id'])
            chapter_map[activity['courseware_id']] = activity['title']

            # 更新请求头
            self.headers['classroom-id'] = cid
            self.headers['xtbz'] = 'ykt'
            self.headers['Referer'] = f'https://changjiang.yuketang.cn/v2/web/studentLog/{cid}'

            # 获取课程详细信息
            data = {'cid': cid, 'new_id': courseware_ids}
            response = requests.post('https://changjiang.yuketang.cn/mooc-api/v1/lms/learn/course/pub_new_pro',
                                   headers=self.headers, data=json.dumps(data)).json()

            # 处理每个课件
            for courseware_id in response['data']:
                url = f'https://changjiang.yuketang.cn/c27/online_courseware/xty/kls/pub_news/{courseware_id}/'
                ret = requests.get(url, headers=self.headers).json()
                
                if ret['success'] == 'False':
                    logging.error(f'获取课程数据失败：{ret}')
                    return
                
                self.process_course_content(ret['data']['content_info'], cid)

if __name__ == "__main__":
    automation = YuKeTangAutomation()
    automation.run()
