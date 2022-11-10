csrftoken = ""  # 需改成自己的
sessionid = ""  # 需改成自己的
uv_id = ""  # 需改成自己的
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
