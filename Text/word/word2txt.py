#将爬取的规范导入为txt文件

import os
from docx import Document

def docx_to_txt(docx_path, txt_path):
    doc = Document(docx_path)
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        for paragraph in doc.paragraphs:
            txt_file.write(paragraph.text + '\n')

def convert_all_docx_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".docx") and not filename.startswith("~$"):
            docx_path = os.path.join(folder_path, filename)
            print(docx_path)
            txt_filename = filename.replace(".docx", ".txt")
            txt_path = os.path.join(folder_path, txt_filename)
            docx_to_txt(docx_path, txt_path)
            print(f"Converted: {docx_path} -> {txt_path}")

if __name__ == "__main__":
    folder_path = r"E:\工作\China\2024实习\LLM\ChatGLM-6B-main\Text\word"  
    convert_all_docx_in_folder(folder_path)
