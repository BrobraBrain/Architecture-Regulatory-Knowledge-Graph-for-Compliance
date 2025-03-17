import pandas as pd
import json
import os
from tqdm import tqdm
import spacy
from spacy.tokens import DocBin
import random

#读取训练文件
with open(r'E:\工作\China\2024实习\LLM\ChatGLM-6B-main\NER\Training_Data\json文件\output.json', 'r',encoding='utf-8') as f:
    data = json.load(f)

entity_name = "KEYWORD"
entity_none = "NONE"

#制作训练集
train_data = data['annotations']    
train_data = [item for item in train_data if any(entity[2] == "KEYWORD" for entity in item[1]["entities"])]

for i in train_data:
    if i[0] == '':
        i[0] = '   '
    train_data = [tuple(i) for i in train_data]

for i in train_data:
    if i[1]['entities'] == []:
        i[1]['entities'] = [(0, 0, entity_name)]
        
    else:
        i[1]['entities'][0] = tuple(i[1]['entities'][0])



# 计算百分之二十的数据量
dev_data_size = int(len(train_data) * 0.10)

# 随机打乱数据顺序
random.shuffle(train_data)

dev_data = train_data[:dev_data_size]
train_data = train_data

# 输出训练集和dev集大小
print(f"训练集大小: {len(train_data)}")
print(f"dev集大小: {len(dev_data)}")

print(train_data)
print(dev_data)

#加载模型
nlp = spacy.load("zh_core_web_lg") 

train_db = DocBin()
dev_db = DocBin()


# 创建doc对象并添加到相应的docbin中
#创建train_data
for text, annot in tqdm(train_data):
    doc = nlp.make_doc(text)
    ents = []
    for start, end, label in annot["entities"]:
        span = doc.char_span(start, end, label=label, alignment_mode="contract")
        if span is None:
            print("Skipping entity")
        else:
            ents.append(span)
    doc.ents = ents
    train_db.add(doc)
    
    
#创建dev_data
for text, annot in tqdm(dev_data):
    doc = nlp.make_doc(text)
    ents = []
    for start, end, label in annot["entities"]:
        span = doc.char_span(start, end, label=label, alignment_mode="contract")
        if span is None:
            print("Skipping entity")
        else:
            ents.append(span)
    doc.ents = ents
    dev_db.add(doc)


# 将docbin对象保存为spacy格式
train_db.to_disk(r"E:\工作\China\2024实习\LLM\ChatGLM-6B-main\NER\docbin\train.spacy")
dev_db.to_disk(r"E:\工作\China\2024实习\LLM\ChatGLM-6B-main\NER\docbin\dev.spacy")




