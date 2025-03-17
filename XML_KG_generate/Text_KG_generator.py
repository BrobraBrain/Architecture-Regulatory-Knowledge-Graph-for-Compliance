import os
import xml.etree.ElementTree as ET
import re
import spacy
import time

# 记录开始时间
start_time = time.time()

# 读取书名列表的txt文档
with open(r'E:\LLM\TEXT\规范demo\book_list\国家规范_demo.txt', 'r', encoding='gbk') as f:
    book_raw_titles = f.readlines()
    book_titles = []
    specification_codes = []
    specification_years = []
    for text in book_raw_titles:
        book_title = text.split(',')[0]
        specification_code = text.split(',')[1]
        specification_year = text.split(',')[2].strip()
        book_titles.append(book_title)
        specification_codes.append(specification_code)
        specification_years.append(specification_year)
  
# 创建XML根元素
root = ET.Element("architecture_specifications_knowledge_graph")

# 加载训练分词模型
nlp = spacy.load(r"E:\工作\China\2024实习\LLM\model_best")

# 遍历每本书
for book_index, book_title in enumerate(book_titles):
    specification = ET.SubElement(root, "specification")
    
    # 创建书籍元素
    specification_id = ET.SubElement(specification, "specification_id")
    specification_id.text = str(book_index + 1)
    
    specification_name = ET.SubElement(specification, "specification_name")
    specification_name.text = book_title

    specification_number = ET.SubElement(specification, "specification_number")
    specification_number.text = specification_codes[book_index]
    
    specification_year = ET.SubElement(specification, "specification_year")
    specification_year.text = specification_years[book_index]
    
    specification_keywords = ET.SubElement(specification, "specification_keywords")
    specification_sections = ET.SubElement(specification, "specification_sections")
    
    item_count = 0  # 用于统计章节关键词或内容
    
    # 打开目录文件(改为储存目录)
    with open(f"E:\工作\China\\2024实习\LLM\ChatGLM-6B-main\Text\\book_directory\{book_title}.txt", "r", encoding='utf-8') as file:
        directory_content = file.readlines()
        print(book_title)
        
        book_keywords = []
        
        for line in directory_content:
            parts = line.split(' ')
            section_number = parts[0].strip()
            section_title = ' '.join(parts[1:]).strip()
            
            book_keywords.append(section_title)
            
            specification_section = ET.SubElement(specification_sections, "section")
            sectionnumber = ET.SubElement(specification_section, "section_number")
            sectionnumber.text = section_number
            
            sectiontitle = ET.SubElement(specification_section, "section_title")
            sectiontitle.text = section_title
            
            sectioncontent = ET.SubElement(specification_section, "section_content")
            sectionkeywords = ET.SubElement(specification_section, "keywords")

            file_path = os.path.join(r"E:\LLM\TEXT\规范demo\content", book_title, f"{section_number}{section_title}.txt")
            section_start_time = time.time()
            with open(file_path, "r", encoding='utf-8') as content_file:
                contents = content_file.read()
                sectioncontent.text = contents
                doc = nlp(contents)
                for ent in doc.ents:
                    keyword_element = ET.SubElement(sectionkeywords, "keyword")
                    keyword_element.text = ent.text
                    item_count += 1  # 每提取一个关键字计数+1
            section_end_time = time.time()
            section_elapsed_time = section_end_time - section_start_time
            print(f"Time taken to process section {section_number}: {section_elapsed_time} seconds")
            
        print(f"Total items extracted from book '{book_title}': {item_count}")
            
        # 计算并打印总耗时
        end_time = time.time()
        total_time = end_time - start_time
        print(f"Total processing time: {total_time} seconds")
# 保存XML文件
tree = ET.ElementTree(root)
tree.write(r"E:\工作\China\2024实习\LLM\ChatGLM-6B-main\knowledge_graph.xml", encoding='utf-8', xml_declaration=True)


