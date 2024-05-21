import os
import random
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
import sys
import shutil

def generate_video(project_name='test', bgm_volume_change=-12):
    # 定义文件路径
    script_dir = os.path.dirname(__file__)
    background_music_path = os.path.join(script_dir, 'temple.m4a')
    project_dir = os.path.join(script_dir, 'Projects', f'{project_name}')
    voice_path = os.path.join(project_dir, 'voice.mp3')
    video_dir = os.path.join(script_dir, 'Resource_Video_Clips')

    # 确保输出目录存在
    os.makedirs(project_dir, exist_ok=True)

    # 获取所有视频文件的路径
    video_paths = [os.path.join(video_dir, f) for f in os.listdir(video_dir) if f.endswith('.mp4')]

    # 加载音频文件
    background_music = AudioSegment.from_file(background_music_path, format='m4a')
    voice = AudioSegment.from_file(voice_path, format='mp3')

    # 调整背景音乐音量
    background_music += bgm_volume_change  # 增加或减少分贝

    # 调整背景音乐长度以匹配人声长度
    if len(background_music) > len(voice):
        background_music = background_music[:len(voice)]
    else:
        background_music = background_music * (len(voice) // len(background_music) + 1)
        background_music = background_music[:len(voice)]

    # 合并音频
    combined_audio = background_music.overlay(voice)

    # 导出合并后的音频到临时文件
    temp_audio_path = os.path.join(project_dir, 'temp_combined_audio.mp3')
    combined_audio.export(temp_audio_path, format='mp3')

    # 加载视频片段并随机选择，直到达到所需的长度
    clips = []
    total_duration = 0
    while total_duration < len(voice) / 1000:  # 将毫秒转换为秒
        clip = VideoFileClip(random.choice(video_paths))
        clips.append(clip)
        total_duration += clip.duration

    # 如果总时长超过了人声长度，裁剪最后一个视频片段
    if total_duration > len(voice) / 1000:
        last_clip = clips[-1]
        clips[-1] = last_clip.subclip(0, last_clip.duration - (total_duration - len(voice) / 1000))

    # 合并视频片段
    final_clip = concatenate_videoclips(clips)

    # 设置视频的音频轨
    audio_clip = AudioFileClip(temp_audio_path)
    final_clip = final_clip.set_audio(audio_clip)

    # 定义临时输出路径，确保路径不包含中文
    temp_output_path = os.path.join(script_dir, 'temp_output.mp4')

    # 导出视频到临时文件
    final_clip.write_videofile(temp_output_path, codec='libx264')

    # 将临时文件移动到最终的包含中文的目录
    output_path = os.path.join(project_dir, f'final_video.mp4')
    shutil.move(temp_output_path, output_path)

    # 清理临时文件
    os.remove(temp_audio_path)


def main():
    # 从命令行参数获取项目名称，默认为'test'
    project_name = sys.argv[1] if len(sys.argv) > 1 else 'test'
    generate_video(project_name)

if __name__ == "__main__":
    main()
