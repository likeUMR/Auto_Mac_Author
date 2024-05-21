import os
import json
from openai import OpenAI

def read_and_truncate(file_path, max_length=5000):
    """从指定路径读取文本，并在必要时截断到最大长度。"""
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    if len(text) > max_length:
        text = text[:max_length]
    return text

def generate_transcript(project_name):
    # 读取配置文件
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, 'config.json')
    
    with open(config_path, 'r') as file:
        config = json.load(file)

    client = OpenAI(api_key=config['openai_api_key'], base_url=config['openai_base_url'])

    # 定义文件路径
    script_dir = os.path.dirname(__file__)
    project_dir = os.path.join(script_dir, 'Projects', project_name)
    prompt_path = os.path.join(script_dir, 'mac_author_prompt.txt')
    template_path = os.path.join(script_dir, 'mac_author_template.txt')
    theme_path = os.path.join(project_dir, 'mac_author_theme.txt')
    rule_path = os.path.join(script_dir, 'mac_author_rule.txt')

    # 读取模板、主题和规则，并在必要时截断
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

    # 保存生成文案到文件
    transcript_path = os.path.join(project_dir, 'transcript.txt')
    with open(transcript_path, 'w', encoding='utf-8') as file:
        file.write(generated_text)

    print("文案生成成功！")
    return generated_text

def main():
    project_name = 'test'
    generate_transcript(project_name)

if __name__ == '__main__':
    main()
