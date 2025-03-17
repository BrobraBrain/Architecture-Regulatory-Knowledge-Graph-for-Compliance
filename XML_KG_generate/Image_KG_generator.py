import docx
import base64
from xml.etree.ElementTree import SubElement
from xml.dom import minidom
import xml.etree.ElementTree as ET
import re
import jieba
import jieba.posseg as pseg
import spacy




jieba.add_word("防火间距", freq=None, tag='n')
jieba.add_word("多层", freq=None, tag='n')
jieba.add_word("高层", freq=None, tag='n')
jieba.add_word("防火分区", freq=None, tag='n')

stop_words = [
    '后来', '比方', '总是', '它', '从', '一边', '很多', '即便', '这些', '部分', '一段', '那个', '建筑',
    '哈', '因而', '特别', '但是', '还是', '这里', '那儿', '至于', '什么', '该', '越过', '如', '假如',
    '她', '那', '除了', '而且', '之后', '纵使', '虽然', '另外', '吧', '确实', '和', '呀', '真的', '只',
    '往', '应该', '继续', '于是', '例如', '大部分', '起来', '关于', '由于', '对于', '可能', '一部分', '比如',
    '这', '然而', '你', '只是', '啊', '比起', '到', '旁边', '接近', '地', '必然', '虽说', '通过', '一下', '这边',
    '就是', '应当', '反而', '这样', '比较', '之前', '一般', '有', '哪边', '就', '就算', '而是', '里', '但',
    '他', '只要', '有些', '如此', '周围', '尽管', '上', '一起', '别的', '此外', '并且', '比如说', '还有', '着',
    '来说', '随着', '哪个', '一直', '来讲', '附近', '却', '同时', '那么', '因此', '始终', '说到', '除此', '朝',
    '较为', '或', '除外', '实际上', '要求', '非常', '以及', '能够', '不过', '一些', '极其', '很', '仅仅', '外',
    '一个', '那样', '而', '之间', '有时候', '再加', '当然', '多数', '距离', '所以', '要', '有时', '一份的', '每个',
    '的确', '如果', '实在', '呢', '还', '绝大部分', '在', '了', '故', '这个', '以至于', '我', '必须', '与', '过',
    '一次', '然后', '接着', '是', '的话', '少数', '一点', '哪里', '一定', '也', '就是说', '那边', '如何', '得', '及',
    '吗', '即使', '却是', '的', '可以', '下', '沿着', '一条', '这儿', '哪些', '因为', '譬如', '那里', '那些', '这么',
    '一种', '设置', '向','建筑','有什么'
]

stop_words = list(set(stop_words))

jieba.add_word("防火间距", freq=None, tag='n')
jieba.add_word("多层", freq=None, tag='n')
jieba.add_word("高层", freq=None, tag='n')
jieba.add_word("防火分区", freq=None, tag='n')

def extract_keywords(content):
    words = pseg.cut(content)
    keyword = [word for word in words if word.word not in stop_words]
    input_keywords = [word.word for word in keyword if word.flag.startswith('n') or word.flag.startswith('l')]
    return input_keywords

#加载分词模型，向量化关键词
nlp = spacy.load(r"E:\工作\China\2024实习\LLM\ChatGLM-6B-main\NER\model_best")

# 读取书名列表的txt文档'
with open(r'E:\LLM\TEXT\规范demo\book_list\国家规范_demo.txt', 'r', encoding='gbk') as f:
    book_raw_titles = f.readlines()
    book_titles = []
    
    
    for text in book_raw_titles:
        book_title = text.split(',')[0]
        book_titles.append(book_title)



def get_content_from_doc(path):
    # 用于存储提取的内容
    extracted_content = []
    extracted_name = []
    extracted_number = []
    extracted_keywords = []
    extracted_keywords_vec = []
    
    # 打开Word文档
    doc = docx.Document(path)
    
    # 初始化标志变量
    flag = False
    pattern = r'(\b表\d+\.\d+\.\d+\b)+(.+)'

    
    # 遍历文档的段落
    for paragraph in doc.paragraphs:
        # 如果找到以“表”开头的行，则提取内容
        if paragraph.text.startswith('表'):
            raw_name = paragraph.text
            matches = re.match(pattern, raw_name)
            if matches:
                number = matches.group(1)
                name = matches.group(2)
                                        
                print("表编号:", number)
                print("描述:", name)

            else:
                number = "未知参数"
                name = "未知名字"
                
            # 标记已找到起始行
            flag = True
            

            continue
        
        # 如果已找到起始行，则提取内容
        if flag:
            for run in paragraph.runs:
                for element in run._element:
                    if element.tag.endswith("drawing"):
                        for blip in element:
                            for drawing in blip.iter("{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}inline"):
                                for blip in drawing.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip"):
                                    # 获取图片的关系 ID
                                    rId = blip.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
                                    # 从关系中获取图片数据
                                    image_part = doc.part.related_parts[rId]
                                    image_data = image_part.blob
                                    # 获取图片base64
                                    base64_image = base64.b64encode(image_data).decode("utf-8")
                                    # 保存图片
                                    extracted_name.append(name)
                                    extracted_number.append(number)
                                    extracted_content.append(base64_image)

                                    
    return zip(extracted_content, extracted_name, extracted_number)                                


root = ET.Element("specifications_picture_knowledge_graph")
for book_title in book_titles:
    specification = ET.SubElement(root, "specification")
    specification.text = book_title

#将图片插入进知识图谱中
    images_data = get_content_from_doc(f"E:\LLM\TEXT\规范demo\word\{book_title}.docx")
    for data, name, number in images_data:
        if number != "未知参数":
            image_element = SubElement(specification, 'image')

        #图片代码xml写入
        
            number_element = SubElement(image_element, 'image_number')
            number_element.text = number     
        
            #图片名称xml写入
            
            name_element = SubElement(image_element, 'image_name')
            name_element.text = name
            
            #图片关键词及向量写入            
            keywords_element = SubElement(image_element, 'keywords')
            
            #加入关键词及关键词的向量
            keywords = extract_keywords(name)
            keywords_vec = []
            for keyword in keywords:
                if keyword:
                    keyword_vector = nlp(keyword).vector
                    keywords_vec.append(keyword_vector)
                        
                        
            for keyword, keyword_vec in zip(keywords, keywords_vec):
                keyword_element = SubElement(keywords_element, 'image_keyword')
                keyword_one = SubElement(keyword_element, 'keyword')
                keyword_one.text = keyword
                
                
                keywordvector_element = SubElement(keyword_element, 'keyword_vector')
                keywordvector_element.text = ','.join(map(str, keyword_vec))
            
            
    
            #图片二进制xml写入
            code_element = SubElement(image_element, 'image_code')
            code_element.text = data

            
            
tree = ET.ElementTree(root)
tree.write(r"E:\LLM\TEXT\规范demo\xml\picture_store.xml", encoding='utf-8', xml_declaration=True)