import requests

def send_post_request(url, data):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Origin': 'http://new.text-to-speech.cn',
        'Referer': 'http://new.text-to-speech.cn/tts/',
        'X-Requested-With': 'XMLHttpRequest'
    }

    # 发送POST请求
    response = requests.post(url, data=data, headers=headers)

    # 检查响应
    if response.status_code == 200:
        print("请求成功，响应内容：")
        print(response.text)
    else:
        print("请求失败，状态码：", response.status_code)

# URL地址
url = "http://new.text-to-speech.cn/wp-content/plugins/speech-tts/getSpeek.php"

# 表单数据
data = {
    'language': '中文（普通话，简体）',
    'voice': 'zh-CN-YunzeNeural',
    'text': '你可将此文本替换为所需的任何文本',
    'role': '0',
    'style': '0',
    'styledegree': '1',
    'volume': '75',
    'predict': '0',
    'rate': '0',
    'pitch': '0',
    'kbitrate': 'audio-16khz-32kbitrate-mono-mp3',
    'silence': '',
    'user_id': '1841'
}

# 调用函数发送POST请求
send_post_request(url, data)
