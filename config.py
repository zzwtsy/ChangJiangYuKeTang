# 以下的csrftoken和sessionid需要改成自己登录后的cookie中对应的字段！！！！而且脚本需在登录雨课堂状态下使用
# 登录上雨课堂，然后按F12-->选Application-->找到雨课堂的cookies，寻找csrftoken和sessionid字段，并复制到下面两行即可
csrftoken = "e1dNh8k1hZQusSFdSRnC8fRZkuWB5xvo"  # 需改成自己的
sessionid = "3qhag2b7569qcrme1n6sg28tkbgq870e"  # 需改成自己的
uv_id = "3461"
select = False  # 是否刷未开放章节的视频 默认不刷
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36',
    'Content-Type': 'application/json',
    'Cookie': 'csrftoken=' + csrftoken + '; sessionid=' + sessionid + '; university_id=' + uv_id + '; platform_id=3',
    'referer': 'https://changjiang.yuketang.cn/v2/web/index',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'university-id': uv_id,
    'uv-id': uv_id,
    'x-csrftoken': csrftoken,
    'xt-agent': 'web',
    'xtbz': 'cloud'
}
leaf_type = {
    "video": 0,
    "homework": 6,
    "exam": 5,
    "recommend": 3,
    "discussion": 4
}
