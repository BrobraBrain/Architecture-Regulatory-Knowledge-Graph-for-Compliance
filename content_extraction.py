import xml.etree.ElementTree as ET
import spacy
from scipy.spatial.distance import cosine
import numpy as np
from model_utils import nlp

tree = ET.parse("/home/fength/fllm/knowledge_graph.xml")
root = tree.getroot()

def extract_content(input_keywords):
    
  question_store = []

  #计算问题的向量
  for question_keyword in input_keywords:
    question_vector = nlp(question_keyword).vector
    question_store.append(question_vector)
  book_similarities = []

  # 提取书本向量
  for book_specification in root.findall(".//specification"):

      #书本比较向量存储初始化
      total_similarity = 0

      for book_keywords in book_specification.findall(".//specification_keywords"):

          #每个问题向量在关键词向量中进行比较
          for question_vector in question_store:
              question_raw_similarities = []
              for book_keyword in book_keywords.findall(".//book_keyword"):
                  book_vector_str = book_keyword.find("book_vector").text

                  if book_vector_str == None or book_vector_str == None:
                      continue
                  book_vector = np.array(book_vector_str.split(","), dtype=float)

                  book_similarity = 1 - cosine(question_vector, book_vector)
                  question_raw_similarities.append(book_similarity)

              #每一个 keyword_input 前四个相似性相加
              question_raw_similarities.sort(reverse=True)
              book_total_similarity = sum(question_raw_similarities[:4]) #此处数字为提取多少个相似性相加
              total_similarity += book_total_similarity

      #依据余弦大小排列 判断书的相关性
      book_similarities.append((book_specification, total_similarity))
  #提取前四本相关规范对象
  book_similarities.sort(key=lambda x: x[1], reverse=True)
  top_books = book_similarities[:3]  #此处数字为返回多少相似规范

  #提取前四本相关规范的知识图谱 xml文件格式
  specifications = [book[0] for book in top_books]


  # 提取章节向量
  ## 每个问题关键词中去比较

  #初始化章节向量比较值
  similarities_compare = []

  for question_vector in question_store:

      #初始化每个问题关键词相似性
      top_similarities = []

      for specification in specifications:

          #返回规范文本信息
          for section in specification.findall(".//section"):


              #返回规范章节关键词余弦值
              for keywords in section.findall(".//keywords"):
                  for keyword_element in keywords.findall(".//keyword_element"):
                      vector_str = keyword_element.find("vector").text
                      if vector_str == None or vector_str == None:
                          continue
                      vector = np.array(vector_str.split(","), dtype=float)

                      #计算章节和问题关键词的余弦相似性
                      similarity = 1 - cosine(question_vector, vector)
                      top_similarities.append(similarity)

              #提取前四个相似的向量值
              top_similarities.sort(reverse=True)
              keyword1_total_similarity = sum(top_similarities[:3])
              similarities_compare.append((specification, section, keyword1_total_similarity))

  #排列比较
  similarities_compare.sort(key=lambda x: x[2], reverse=True)


  #选取其中的内容进行返回
  top_20_similar_contents = [section.find("section_content").text for specification, section, _ in similarities_compare[:15]]
  top_20_similar_title = [section.find("section_title").text for specification, section, _ in similarities_compare[:15]]
  top_20_similar_book_name = [specification.find("specification_name").text for specification, section, _ in similarities_compare[:15]]
  top_20_similar_book_number = [specification.find("specification_number").text for specification, section, _ in similarities_compare[:15]]

    
  all_content = zip(top_20_similar_contents, top_20_similar_title, top_20_similar_book_name, top_20_similar_book_number)
  return all_content
