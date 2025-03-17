import base64
from xml.etree.ElementTree import parse
from sklearn.metrics.pairwise import cosine_similarity
from keyword_extraction import extract_keywords
from model_utils import nlp
import numpy as np

tree2 = parse("/home/fength/fllm/picture_knowledge_graph.xml")
root2 = tree2.getroot()


def picture_store(question):
    pictures_data = []
    pictures_name = []
    pictures_number = []
    question_vectors = []
    best_match_image = None

    # 提取问题的关键词向量
    question_keywords = extract_keywords(question)
    print(question_keywords)
    for question_keyword in question_keywords:
        question_vec = nlp(question_keyword).vector
        question_vectors.append(question_vec)
    
    # 计算问题关键词向量的平均值
    if question_vectors:
        question_vector = np.mean(question_vectors, axis=0)
    else:
        question_vector = np.zeros(nlp.vocab.vectors_length)  # 如果没有找到关键词向量，使用零向量

    # 从 XML 文件中提取所有图片的关键词向量
    image_vectors = []
    images = []

    for specification in root2.findall("specification"):
        for image in specification.findall("image"):
            images.append(image)
            keyword_vectors = []
            for keyword in image.findall("keywords/image_keyword/keyword_vector"):
                keyword_vector = np.array([float(x) for x in keyword.text.split(",")])
                keyword_vectors.append(keyword_vector)
            
            # 计算平均关键词向量
            if keyword_vectors:
                avg_keyword_vector = np.mean(keyword_vectors, axis=0)
                image_vectors.append(avg_keyword_vector)

    # 计算余弦相似度
    cosine_similarities = cosine_similarity([question_vector], image_vectors).flatten()

    # 找到相似度最高的图片
    highest_similarity_index = cosine_similarities.argmax()
    best_match_image = images[highest_similarity_index]
                    
    if best_match_image is not None:
        
            
        image_name = best_match_image.find("image_name").text

        for specification in root2.findall("specification"):
            for image_list in specification.findall("image"):
                for image_compare in image_list.findall("image_name"):
                    image_compare = image_compare.text

                    if image_compare == image_name:
                        image_code = image_list.find("image_code").text
                        image_number = image_list.find("image_number").text

                        pictures_data.append(image_code)
                        pictures_name.append(image_compare)
                        pictures_number.append(image_number)

        return pictures_data, pictures_name, pictures_number