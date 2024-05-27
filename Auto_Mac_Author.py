import os
import re
import time
from generate_transcript import generate_transcript
from generate_audio import generate_audio
from generate_video import generate_video
from get_hot_board import fetch_top_videos
from generate_video_info import generate_video_info
import sys
sys.path.append('/home/umr/social-auto-upload/examples/')
from upload_video_to_douyin import upload_videos

def clean_title(title):
    # 使用正则表达式提取汉字和英文字符
    clean_title = re.findall(r'[\u4e00-\u9fa5A-Za-z]', title)
    return ''.join(clean_title[:5])  # 返回前五个字符

def main(item=3,start=0):
    print("开始生成项目内容。")
    videos = fetch_top_videos(item,start)

    for video in videos:
        # 提取和清理标题
        cleaned_title = clean_title(video['title'])

        # 创建项目文件夹
        timestamp = time.strftime("%Y%m%d", time.localtime())
        project_name = f"{timestamp}_{cleaned_title}"
        script_dir = os.path.dirname(__file__)
        project_dir = os.path.join(script_dir, 'Projects', project_name)
        os.makedirs(project_dir, exist_ok=True)

        # 创建并写入文件
        file_path = os.path.join(project_dir, "mac_author_theme.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            content_lines = [
                f"标题：{video['title']}",
                f"主题: {video['tname']}",
                f"UP主: {video['owner']}",
                f"简介：{video['desc'] if len(video['desc']) >= 8 else ''}",
                f"动态：{video['dynamic'] if len(video['dynamic']) >= 8 else ''}",
                f"内容：{video['summary'] if video['summary'] != 'No summary available' else ''}"
                f"热评：{video['hot_comment']['username']}：{video['hot_comment']['message']}"
            ]
            file.write("\n".join(content_lines))

        # 检查文件内容是否有效
        if video['summary'] == 'No summary available':
            os.remove(file_path)
            os.rmdir(project_dir)
            print(f"无效内容，已删除项目文件夹：{project_dir}")
            continue

        # 生成文案
        print(f"正在为项目 {project_name} 生成文案...")
        generate_transcript(project_dir,split=True)

        # 生成音频
        print(f"正在为项目 {project_name} 生成音频...")
        generate_audio(project_dir)

        # 生成视频
        print(f"正在为项目 {project_name} 生成视频...")
        generate_video(project_dir)

        # 生成视频信息
        print(f"正在为项目 {project_name} 生成视频信息...")
        generate_video_info(project_name)


        print(f"项目 {project_name} 的所有生成工作已完成。")
        print("开始上传视频到抖音...")
        upload_videos(project_dir)
        print("视频上传完成。")

if __name__ == "__main__":
    main(3,1) #para1：总生成视频数 para2：起始视频序号（0表示从热榜第一开始，n表示从热榜n+1开始）
