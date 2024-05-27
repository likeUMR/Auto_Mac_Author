import os
import json
from openai import OpenAI
import re

def generate_video_info(project_name):
    # 定义文件路径
    script_dir = os.path.dirname(__file__)
    project_dir = os.path.join(script_dir, 'Projects', project_name)
    info_dir = os.path.join(project_dir, 'final_video.txt')
    transcript_path = os.path.join(project_dir, 'transcript.txt')
    author_theme_path = os.path.join(project_dir, 'mac_author_theme.txt')
    
    # 从transcript.txt读取标题
    with open(transcript_path, 'r', encoding='utf-8') as file:
        transcript_content = file.read()
    
    # 使用正则表达式查找标题
    match = re.search(r'《(.+?)传奇》', transcript_content)
    if match:
        title_part = match.group(1)  # 提取标题的动态部分
    else:
        title_part = "这什么东西"

    # 从mac_author_theme.txt读取 UP主 信息
    up_zhu_tag = "神秘人"
    with open(author_theme_path, 'r', encoding='utf-8') as file:
        author_content = file.read()
        match = re.search(r'UP主: (.+)', author_content)
        if match:
            up_zhu_tag = match.group(1).strip()  # 提取 UP主 的名称
    
    # 定义固定的标题和 hashtags
    title = f"麦克阿瑟：大型纪录片之《{title_part}传奇》"
    
    # 使用集合来避免重复的 hashtags
    hashtags_set = {"麦克阿瑟", "大型纪录片", title_part, "鬼畜恶搞", up_zhu_tag}
    hashtags = ' '.join(f"#{tag}" for tag in hashtags_set)  # 生成不重复的 hashtags 字符串
    
    # 写入到 txt 文件
    with open(info_dir, 'w', encoding='utf-8') as f:
        f.write(title + '\n')
        f.write(hashtags + '\n')

    print(f"文件 '{info_dir}' 已创建，包含标题和 hashtags。")

def main():
    project_name = '20240526_原神动画短'
    generate_video_info(project_name)


if __name__ == '__main__':
    main()
