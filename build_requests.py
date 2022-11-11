import requests

from main import headers
from watch_video import one_video_watcher


def get_class_info_dict(cid, VideoId, name):
    get_url = 'https://changjiang.yuketang.cn/mooc-api/v1/lms/learn/leaf_info/%s/%s/' % (cid, VideoId)
    response = requests.get(url=get_url, headers=headers).json()
    skuid = response['data']['sku_id']
    # ccid = response['data']['content_info']['media']['ccid']
    user_id = response['data']['user_id']
    course_id = response['data']['course_id']
    one_video_watcher(VideoId, name, course_id, str(user_id), cid, skuid)
