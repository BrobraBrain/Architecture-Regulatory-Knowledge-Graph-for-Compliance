

import pandas as pd
import json
import os
from tqdm import tqdm
import spacy
from spacy.tokens import DocBin
import random

#读取训练文件
with open(r'E:\工作\China\2024实习\LLM\ChatGLM-6B-main\Text\Json\annotations1.json', 'r',encoding='utf-8') as f:
    data = json.load(f)

entity_name = "KEYWORD"
entity_none = "NONE"

#制作训练集
train_data = data['annotations']
train_data = [item for item in train_data if item[1] and "entities" in item[1] and any(entity[2] == "KEYWORD" for entity in item[1]["entities"])]



for i in train_data:
    if i[1]['entities'] == []:
        i[1]['entities'] = (0, 0, entity_name)
        
    elif len(i[1]['entities']) !=1 :
        i[1]['entities'] = i[1]['entities'][1]
        
        i[0] = i[0].replace('\r', '')
        
    else:
        i[1]['entities'][0] = i[1]['entities'][0]
        i[0] = i[0].replace('\r', '')

print(train_data)
        












