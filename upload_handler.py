import fitz  # PyMuPDF
import os
import re
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import jieba
from http import HTTPStatus
import dashscope


# API_KEY记得改！！！要收费, 在阿里云
#申请KEY调用API
#后续调整好环境后本地部署视觉大模型

dashscope.api_key = "YOUR API_KEY HERE" #输入你的API_KEY

#视觉语言模型使用
def simple_multimodal_conversation_call(file_path):

    messages = [
        {
            "role": "user",
            "content": [
                {"image": f"{file_path}"},
                {"text": "please use Chinese to describe the content in picture"}
            ]
        }
    ]
    response = dashscope.MultiModalConversation.call(model='qwen-vl-plus',
                                                     messages=messages)
    if response.status_code == HTTPStatus.OK:
        text_content = response['output']['choices'][0]['message']['content'][0]['text']
        return text_content
    else:
        raise ValueError("No such picture file")


# 使用 jieba 进行中文分词
def tokenize(text):
    return " ".join(jieba.lcut(text))


# 返回文件的后缀名
def determine_file_type(file_path):
    _, file_extension = os.path.splitext(file_path)
    return file_extension.lower()

def extract_text_and_images_with_captions(pdf_path):
    # 打开PDF文档
    pdf_document = fitz.open(pdf_path)
    
    # 用于存储文字和图片
    text_by_paragraphs = []

    # 遍历每一页
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        # 提取文字并按段落分段
        text = page.get_text("text")
        paragraphs = text.split('。\n')  # 假设段落之间有双换行符
        for paragraph in paragraphs:
            # 去掉段落中的空格和换行符
            cleaned_paragraph = re.sub(r'\s+', ' ', paragraph).strip()
            text_by_paragraphs.append(cleaned_paragraph)

    return text_by_paragraphs



#提取word文档的句子
def extract_word_content(doc_path):
    doc = Document(doc_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
        #将word获取为字符串
        str_full_text = "\n".join(full_text)\
        #把每一段分为一个段落
        split_text = str_full_text.split('。\n') 
    return split_text


#查询和prompt相似的句子
def find_file_similarity(documents, question):
    #集合成一个str
    reference = ""
    # 对文档进行分词
    tokenized_documents = [tokenize(doc) for doc in documents]
    tokenized_query = tokenize(question)

    # 将文档和查询分别转化为TF-IDF向量
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(tokenized_documents)

    # 查询向量化
    query_vec = vectorizer.transform([tokenized_query])

    # 计算查询向量与文档向量之间的余弦相似度
    cosine_similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()

    # 获取前五个最相似文档的索引
    top_n = 5
    top_indices = np.argsort(cosine_similarities)[-top_n:][::-1]

    # 输出前五个最相似的文档
    print(f"前五个最相似的文档是：")
    for index in top_indices:
        reference.join(documents[index])
        #验证收录的文章相似性的是什么
        print(f"Document {index} with similarity score {cosine_similarities[index]}: {documents[index]}")
        print("----------------------------------------------------")
        return reference
        
        

#启动程序
def upload_file_keyword(file_path, question):
    file_name_with_extension = os.path.basename(file_path)
    file_name = os.path.splitext(file_name_with_extension)[0]
    file_type = determine_file_type(file_path)
    
    # 打印文件名称
    print(f"Processing file: {file_name}") 
       
    
    #如果输入是pdf格式
    if file_type == '.pdf':
        print("This is a PDF file.")
        #提取文字
        documents = extract_text_and_images_with_captions(file_path)
        # 打印提取的文字段落
        file_reference =  find_file_similarity(documents, question)
        
        print("找到PDF相似的问题")
        return file_reference

        
    #如果输入时doc或则docx格式    
    elif file_type in ['.doc', '.docx']:
        print("This is a Word file.")
        word_content = extract_word_content(file_path)
        # 打印提取的文字段落
        file_reference = find_file_similarity(word_content, question)
        print("找到doc相似的问题")
        return file_reference

        
    #如果输入是图片格式
    elif file_type in ['.jpg', '.jpeg', '.png']:
        file_reference = simple_multimodal_conversation_call(file_path)
        print("找到jpg相似的问题")
        return file_reference
        
    #如果是其他格式    
    else:
        raise ValueError("Unsupported file type")
