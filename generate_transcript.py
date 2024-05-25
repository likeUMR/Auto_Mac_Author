import os
import json
from openai import OpenAI
import re

def read_and_truncate(file_path, max_length=5000):
    """从指定路径读取文本，并在必要时截断到最大长度。"""
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    if len(text) > max_length:
        text = text[:max_length]
    return text

def smart_split(text, desired_length=7):
    # 定义分割标点
    punctuation = '，。？！,?!;；:：'
    segments = []
    current_segment = ""
    i = 0  # 增加一个索引变量来追踪当前字符的位置

    while i < len(text):
        char = text[i]
        current_segment += char

        if char in punctuation:
            if len(current_segment) >= desired_length:
                # 在添加前移除尾部的标点符号
                segments.append(current_segment.strip(punctuation).strip())
                current_segment = ""
            else:
                # 查找下一个标点符号的位置
                next_punct = -1
                for j in range(i + 1, len(text)):
                    if text[j] in punctuation:
                        next_punct = j
                        break
                
                # 如果找到下一个标点，并且下一个标点之前的长度不超过期望长度加5
                if next_punct != -1 and (next_punct - i + len(current_segment)) <= desired_length + 5:
                    current_segment += text[i + 1:next_punct + 1]
                    i = next_punct  # 更新索引到下一个标点
                # 在添加前移除尾部的标点符号
                segments.append(current_segment.strip(punctuation).strip())
                current_segment = ""
        i += 1  # 更新索引

    # 检查最后是否还有剩余字符未处理
    if current_segment:
        segments.append(current_segment.strip(punctuation).strip())

    return segments



def generate_transcript(project_name, split=False):
    # 读取配置文件
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, 'config.json')
    
    with open(config_path, 'r') as file:
        config = json.load(file)

    client = OpenAI(api_key=config['openai_api_key'], base_url=config['openai_base_url'])

    # 定义文件路径
    script_dir = os.path.dirname(__file__)
    project_dir = os.path.join(script_dir, 'Projects', project_name)
    transcript_dir = os.path.join(project_dir, 'transcript')
    os.makedirs(transcript_dir, exist_ok=True)

    prompt_path = os.path.join(script_dir, 'mac_author_prompt.txt')
    template_path = os.path.join(script_dir, 'mac_author_template.txt')
    theme_path = os.path.join(project_dir, 'mac_author_theme.txt')
    rule_path = os.path.join(script_dir, 'mac_author_rule.txt')

    # 读取模板、主题和规则
    template = read_and_truncate(template_path)
    theme = read_and_truncate(theme_path)
    rule = read_and_truncate(rule_path)

    # 读取并替换 prompt
    with open(prompt_path, 'r', encoding='utf-8') as file:
        prompt = file.read()
    prompt = prompt.replace('{{{template}}}', template)
    prompt = prompt.replace('{{{theme}}}', theme)
    prompt = prompt.replace('{{{rule}}}', rule)

    # 请求模型生成文案
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": prompt}]
    )

    # 获取生成的文案
    generated_text = response.choices[0].message.content
    # print(generated_text)

    # 保存生成文案到文件
    if not split:
        transcript_path = os.path.join(transcript_dir, 'transcript.txt')
        with open(transcript_path, 'w', encoding='utf-8') as file:
            file.write(generated_text)
    else:
        transcript_path = os.path.join(project_dir, 'transcript.txt')
        with open(transcript_path, 'w', encoding='utf-8') as file:
            file.write(generated_text)
        parts = smart_split(generated_text)
        for i, part in enumerate(parts):
            part_file_path = os.path.join(transcript_dir, f'transcript_{i}.txt')
            with open(part_file_path, 'w', encoding='utf-8') as file:
                file.write(part)

    print("文案生成成功！")
    return generated_text

def main():
    project_name = 'test'
    generate_transcript(project_name,split=True)

if __name__ == '__main__':
    main()
