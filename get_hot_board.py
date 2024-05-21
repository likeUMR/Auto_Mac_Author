from functools import reduce
from hashlib import md5
import urllib.parse
import time
import requests

mixinKeyEncTab = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
    33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
    61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
    36, 20, 34, 44, 52
]

def getMixinKey(orig: str):
    '对 imgKey 和 subKey 进行字符顺序打乱编码'
    return reduce(lambda s, i: s + orig[i], mixinKeyEncTab, '')[:32]

def encWbi(params: dict, img_key: str, sub_key: str):
    '为请求参数进行 wbi 签名'
    mixin_key = getMixinKey(img_key + sub_key)
    curr_time = round(time.time())
    params['wts'] = curr_time                                   # 添加 wts 字段
    params = dict(sorted(params.items()))                       # 按照 key 重排参数
    # 过滤 value 中的 "!'()*" 字符
    params = {
        k : ''.join(filter(lambda chr: chr not in "!'()*", str(v)))
        for k, v 
        in params.items()
    }
    query = urllib.parse.urlencode(params)                      # 序列化参数
    wbi_sign = md5((query + mixin_key).encode()).hexdigest()    # 计算 w_rid
    params['w_rid'] = wbi_sign
    return params

def getWbiKeys() -> tuple[str, str]:
    '获取最新的 img_key 和 sub_key'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://www.bilibili.com/'
    }
    resp = requests.get('https://api.bilibili.com/x/web-interface/nav', headers=headers)
    resp.raise_for_status()
    json_content = resp.json()
    img_url: str = json_content['data']['wbi_img']['img_url']
    sub_url: str = json_content['data']['wbi_img']['sub_url']
    img_key = img_url.rsplit('/', 1)[1].split('.')[0]
    sub_key = sub_url.rsplit('/', 1)[1].split('.')[0]
    return img_key, sub_key



def fetch_bilibili_summary(bvid,up_mid,cid):
    img_key, sub_key = getWbiKeys()
    params = {
        'bvid': bvid,
        'cid': cid,  # 示例 CID，根据实际情况可能需要动态获取
        'up_mid': up_mid,  # 示例 UP主 ID，根据实际情况可能需要动态获取
        'web_location': '333.788',  # 示例位置，可能需要调整
    }
    signed_params = encWbi(params, img_key, sub_key)
    url = "https://api.bilibili.com/x/web-interface/view/conclusion/get"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://www.bilibili.com'
    }

    response = requests.get(url, params=signed_params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['code'] == 0 and 'summary' in data['data']['model_result']:
            return data['data']['model_result']['summary']
    return "No summary available"

def fetch_top_videos(item=3,start=0):
    url = "https://api.bilibili.com/x/web-interface/ranking/v2"
    params = {
        'rid': 0,
        'type': 'all',
        'web_location': '333.934',
        'w_rid': '65e4fb19a08da3fec24dca1a46817a89',
        'wts': '1716217767'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://www.bilibili.com'
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['code'] == 0:
            top_videos = data['data']['list'][start:item+start]  # 获取前5个视频条目
            simplified_data = []
            for video in top_videos:
                video_info = {
                    'bvid': video['bvid'],
                    'title': video['title'],
                    'desc': video['desc'],
                    'dynamic': video['dynamic'],
                    'summary': fetch_bilibili_summary(video['bvid'],video['owner']['mid'],video['cid']) , # 调用摘要函数
                    'tname': video['tname']
                }
                simplified_data.append(video_info)
            return simplified_data
    return []

if __name__ == "__main__":
    top_videos = fetch_top_videos()
    for video in top_videos:
        print(video)
