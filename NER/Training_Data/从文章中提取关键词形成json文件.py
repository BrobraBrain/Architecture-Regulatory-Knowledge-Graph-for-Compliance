import json
import re
from docx import Document


def read_keywords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    keywords = [keyword.strip() for keyword in content.split(',') if keyword.strip()]
    keywords = list(set(keywords))
    return keywords

def read_docx(file_path):
    doc = Document(file_path)
    sentences = []
    for para in doc.paragraphs:
        sentences.extend(re.split(r'(?<=。|！|？)', para.text))
    return sentences

def find_keywords_in_sentence(sentence, keywords):
    entities = []
    for keyword in keywords:
        start = sentence.find(keyword)
        if start != -1:
            entities.append([start, start + len(keyword), "KEYWORD"])
    return entities

def create_json_data(sentences, keywords):
    data = {"classes": ["KEYWORD"], "annotations": []}
    for sentence in sentences:
        entities = find_keywords_in_sentence(sentence, keywords)
        if entities:
            for entity in entities:
                if entity:
                    data["annotations"].append([sentence, {"entities": [entity]}])
        else:
            pass
    return data

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# 文件路径
keywords_file_path = r'E:\工作\China\2024实习\LLM\ChatGLM-6B-main\NER\Training_Data\json文件\keywords_list.txt'
docx_file_path = r'E:\工作\China\2024实习\LLM\ChatGLM-6B-main\Text\word\建筑设计防火规范[附条文说明].docx'
output_json_file_path = r'E:\工作\China\2024实习\LLM\ChatGLM-6B-main\NER\Training_Data\json文件\output.json'

# 读取关键词列表和Word文档
keywords = read_keywords(keywords_file_path)
sentences = read_docx(docx_file_path)

# 生成JSON数据
json_data = create_json_data(sentences, keywords)

# 保存JSON数据到文件
save_json(json_data, output_json_file_path)
print("JSON文件已生成:", output_json_file_path)