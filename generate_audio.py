import requests
import os
import json
import time
from pathlib import Path
import re

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.json')
    with open(config_path, 'r') as file:
        return json.load(file)

def login_and_get_cookies(username, password):
    login_url = 'http://new.text-to-speech.cn/wp-admin/admin-ajax.php'
    login_data = {
        'action': 'user_login',
        'username': username,
        'password': password,
        'rememberme': '1'
    }
    session = requests.Session()
    response = session.post(login_url, data=login_data)
    if response.status_code == 200:
        cookies = session.cookies.get_dict()
        cookies.pop('PHPSESSID', None)  # Remove PHPSESSID
        return session.cookies.get_dict()
    else:
        return None

def save_cookies(cookies, path):
    with open(path, 'w') as file:
        json.dump(cookies, file)

def load_cookies(path):
    try:
        with open(path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return None

def save_last_attempt_time(path):
    with open(path, 'w') as file:
        file.write(str(time.time()))

def get_last_attempt_time(path):
    try:
        with open(path, 'r') as file:
            return float(file.read())
    except FileNotFoundError:
        return None

def generate_audio(project_name):
    config = load_config()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.join(script_dir, 'Projects', project_name)
    transcript_dir = os.path.join(project_dir, 'transcript')
    voice_dir = os.path.join(project_dir, 'voice')

    if not os.path.exists(voice_dir):
        os.makedirs(voice_dir)

    transcript_files = [f for f in os.listdir(transcript_dir) if f.endswith('.txt')]
    if not transcript_files:
        print("No transcript files found.")
        return

    cookies = load_cookies(os.path.join(script_dir, 'cookies.json'))
    last_attempt_path = os.path.join(script_dir, 'last_attempt.txt')
    last_attempt_time = get_last_attempt_time(last_attempt_path)
    current_time = time.time()

    if not cookies:
        if last_attempt_time and current_time - last_attempt_time < 3600:
            print("Recently failed login attempt, try again later.")
            return
        cookies = login_and_get_cookies(config['ttl_username'], config['ttl_password'])
        if cookies:
            save_cookies(cookies, os.path.join(script_dir, 'cookies.json'))
            save_last_attempt_time(last_attempt_path)
        else:
            print("Failed to login and get cookies.")
            save_last_attempt_time(last_attempt_path)
            return

    cookie_str = '; '.join([f'{key}={value}' for key, value in cookies.items()])
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Origin': 'http://new.text-to-speech.cn',
        'Referer': 'http://new.text-to-speech.cn/tts/',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': cookie_str
    }

    url = "http://new.text-to-speech.cn/wp-content/plugins/speech-tts/getSpeek.php"

    for transcript_file in transcript_files:
        transcript_path = os.path.join(transcript_dir, transcript_file)
        with open(transcript_path, 'r', encoding='utf-8') as file:
            text = file.read()

        data = {
            'language': '中文（普通话，简体）',
            'voice': 'zh-CN-YunzeNeural',
            'text': text,
            'role': '0',
            'style': '0',
            'styledegree': '1',
            'volume': '75',
            'predict': '0',
            'rate': '0',
            'pitch': '0',
            'kbitrate': 'audio-48khz-192kbitrate-mono-mp3',
            'silence': '',
            'replice': '1',
        }

        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            if response_data['code'] == 200:
                print(f"语音生成成功，开始下载 {transcript_file}...")
                download_url = response_data['download']
                match = re.search(r'_(\d+)', Path(transcript_file).stem)
                id_number = int(match.group(1)) if match else -1
                download_file(download_url, voice_dir, id=id_number)
            else:
                print(f"语音生成失败：{response_data['msg']}")
                # if response_data['msg'] == 'Invalid session or cookies':
                os.remove(os.path.join(script_dir, 'cookies.json'))  # Remove old cookies file
                print("Trying to re-login and fetch new cookies...")
                generate_audio(project_name)  # Retry with new login
        else:
            print("请求失败，状态码：", response.status_code)

def download_file(url, output_folder, id=-1):
    if id > -1:
        local_filename = f'voice_{id}.mp3'
    else:
        local_filename = 'voice.mp3'
    full_path = os.path.join(output_folder, local_filename)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(full_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"文件已下载到：{full_path}")

if __name__ == "__main__":
    project_name = "test"
    generate_audio(project_name)
