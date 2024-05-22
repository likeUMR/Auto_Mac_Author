import os
import random
import shutil
import subprocess
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
from pydub import AudioSegment

from moviepy.editor import VideoFileClip, AudioFileClip

def merge_video_and_audio(video_path, audio_path, output_path):
    # 加载视频文件，不包括音频
    video_clip = VideoFileClip(video_path, audio=False)
    
    # 加载音频文件
    audio_clip = AudioFileClip(audio_path)
    
    # 将音频设置到视频剪辑中
    video_clip = video_clip.set_audio(audio_clip)
    
    # 导出合并后的视频文件
    video_clip.write_videofile(output_path, codec='libx264')
    
    # 关闭打开的剪辑以释放资源
    video_clip.close()
    audio_clip.close()
    
    print("Video and audio have been merged.")


def add_subtitles(video_path, subtitles_path, output_path):
    style_options = (
        "Fontname=Microsoft YaHei,"
        "Fontsize=30,"
        "PrimaryColour=&H00ffffff,"  # 白色
        "OutlineColour=&H00000000,"  # 黑色
        "Outline=1,"
        "BackColour=&H00000000,"  # 半透明黑色
        "Alignment=2"  # 底部居中
    )
    
    command = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f"subtitles='{subtitles_path}':force_style='{style_options}'",
        '-c:v', 'libx264',
        '-c:a', 'copy',
        '-y', output_path
    ]
    subprocess.run(command, check=True)
    print("Subtitles with customized styles have been added to the video.")


def format_time(ms):
    """ Helper function to format milliseconds to SRT time format """
    hours = int(ms / 3600000)
    minutes = int((ms % 3600000) / 60000)
    seconds = int((ms % 60000) / 1000)
    milliseconds = int(ms % 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def setup_directories(project_name):
    script_dir = os.path.dirname(__file__)
    project_dir = os.path.join(script_dir, 'Projects', project_name)
    os.makedirs(project_dir, exist_ok=True)
    return script_dir, project_dir


def load_and_combine_audio(voice_dir, transcript_dir):
    voice_files = sorted([f for f in os.listdir(voice_dir) if f.endswith('.mp3')],
                         key=lambda x: int(x.split('_')[-1].split('.')[0]) if '_' in x else 0)
    combined_voice = AudioSegment.empty()
    subtitles = []
    total_length = 0  # Track total length of all audio for subtitles timing

    for vf in voice_files:
        voice_path = os.path.join(voice_dir, vf)
        file_id = vf.split('_')[-1].split('.')[0]
        transcript_path = os.path.join(transcript_dir, f"transcript_{file_id}.txt")
        voice = AudioSegment.from_file(voice_path, format='mp3')
        with open(transcript_path, 'r', encoding='utf-8') as file:
            transcript_text = file.read().strip()

        combined_voice += voice
        start_time = total_length
        end_time = total_length + len(voice)
        subtitles.append((start_time, end_time, transcript_text))
        total_length += len(voice)

    return combined_voice, subtitles

def generate_srt_file(subtitles, srt_path):
    with open(srt_path, 'w', encoding='utf-8') as srt_file:
        for idx, (start, end, text) in enumerate(subtitles, 1):
            srt_file.write(f"{idx}\n")
            srt_file.write(f"{format_time(start)} --> {format_time(end)}\n")
            srt_file.write(f"{text}\n\n")

def combine_audio(background_music_path, combined_voice, bgm_volume_change):
    background_music = AudioSegment.from_file(background_music_path, format='m4a')
    background_music += bgm_volume_change
    if len(background_music) > len(combined_voice):
        background_music = background_music[:len(combined_voice)]
    else:
        background_music = background_music * (len(combined_voice) // len(background_music) + 1)
        background_music = background_music[:len(combined_voice)]

    combined_audio = background_music.overlay(combined_voice)
    return combined_audio

def select_and_concatenate_clips(video_dir, audio_length):
    video_paths = [os.path.join(video_dir, f) for f in os.listdir(video_dir) if f.endswith('.mp4')]
    clips = []
    total_duration = 0

    while total_duration < audio_length:
        video_path = random.choice(video_paths)
        clip = VideoFileClip(video_path)
        clips.append(clip)
        total_duration += clip.duration

    if total_duration > audio_length:
        last_clip = clips[-1]
        excess_duration = total_duration - audio_length
        clips[-1] = last_clip.subclip(0, last_clip.duration - excess_duration)

    final_clip = concatenate_videoclips(clips)
    return final_clip



def generate_video(project_name='test', bgm_volume_change=-12):
    script_dir, project_dir = setup_directories(project_name)
    voice_dir = os.path.join(project_dir, 'voice')
    transcript_dir = os.path.join(project_dir, 'transcript')
    video_dir = os.path.join(script_dir, 'Resource_Video_Clips')
    background_music_path = os.path.join(script_dir, 'temple.m4a')

    combined_voice, subtitles = load_and_combine_audio(voice_dir, transcript_dir)
    srt_path = os.path.join(project_dir, 'subtitles.srt')
    generate_srt_file(subtitles, srt_path)

    combined_audio = combine_audio(background_music_path, combined_voice, bgm_volume_change)
    temp_audio_path = os.path.join(script_dir, 'temp_combined_audio.mp3')
    combined_audio.export(temp_audio_path, format='mp3')

    audio_length = len(combined_voice) / 1000  # Convert to seconds
    final_clip = select_and_concatenate_clips(video_dir, audio_length)
    temp_video_path = os.path.join(script_dir, 'temp_video.mp4')
    final_clip.write_videofile(temp_video_path, codec='libx264')

    # Assuming merge_video_and_audio and add_subtitles are defined elsewhere
    merged_video_path = os.path.join(script_dir, 'merged_video.mp4')
    temp_output_video_path = os.path.join(script_dir, 'final_video.mp4')
    merge_video_and_audio(temp_video_path, temp_audio_path, merged_video_path)
    add_subtitles(merged_video_path, srt_path, temp_output_video_path)

    # 将临时文件移动到最终的包含中文的目录
    output_path = os.path.join(project_dir, f'final_video.mp4')
    shutil.move(temp_output_video_path, output_path)

    # Cleanup
    os.remove(temp_video_path)
    os.remove(temp_audio_path)
    os.remove(srt_path)
    os.remove(merged_video_path)



def main():
    # 从命令行参数获取项目名称，默认为'test'
    project_name =  'test'
    generate_video(project_name)

if __name__ == "__main__":
    main()

