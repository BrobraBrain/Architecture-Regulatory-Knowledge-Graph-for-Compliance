from docx import Document
import os
import re


#读取建筑规范的书名
with open(r'E:\LLM\TEXT\规范demo\book_list\国家规范_demo.txt', 'r', encoding='gbk') as f:
    book_raw_titles = f.readlines()
    book_titles = []
    for text in book_raw_titles:
        book_title = text.split(',')[0]
        print(book_title)
        
        
        names = []
        # 读取章节名字的txt文件
        with open(rf'E:\LLM\TEXT\规范demo\book_directory\{book_title}.txt', encoding='utf-8') as f:
            chapter_names = f.readlines()
            for chapter_name in chapter_names:
                chapter_name = re.sub(r'\s', '', chapter_name)
                
                names.append(chapter_name)

        # 打开Word文档
        doc = Document(rf'E:\LLM\TEXT\规范demo\word\{book_title}.docx')

        # 初始化当前章节名和章节内容列表
        current_chapter_name = None
        chapter_content = []
        # 要创建的目录路径
        directory_path = rf'E:\LLM\TEXT\规范demo\content\{book_title}'

        # 创建目录
        os.makedirs(directory_path, exist_ok=True)
        
        # 遍历Word文档的段落
        for para in doc.paragraphs:
            # 如果当前段落的文本在章节名列表中
            para = re.sub(r'\s', '', para.text)
            para = re.sub(r'\(', '（', para)
            para = re.sub(r'\)', '）', para)
            if para in names:
                print("成功了")
                # 如果当前章节不为空，则将当前章节内容写入文件
                if current_chapter_name is not None:
                    
                    file_name = f"E:\LLM\TEXT\规范demo\content\{book_title}\{current_chapter_name}.txt"
                    with open(file_name, "w", encoding="utf-8") as file:
                        file.write("\n".join(chapter_content))
                        print(chapter_content)
                        chapter_content = []
                        
                
                # 更新当前章节名，并清空章节内容列表
                current_chapter_name = para.strip()
                
            else:
                # 将段落内容添加到当前章节的内容列表中
                chapter_content.append(para)

        # 写入最后一个章节的内容到文件
        if current_chapter_name is not None:
            file_name = f"E:\LLM\TEXT\规范demo\content\{book_title}\{current_chapter_name}.txt"
            with open(file_name, "w", encoding="utf-8") as file:
                file.write("\n".join(chapter_content))


