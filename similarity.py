from sentence_transformers import SentenceTransformer, util
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jieba


# 使用 jieba 进行中文分词
def tokenize(text):
    return " ".join(jieba.lcut(text))

def similarity_find(question, raw_content):
    similarities = []
    matches_picture = []
    for contents, titles, book_names, book_numbers in raw_content:
        if contents != None:
            
            contents = re.split(r'。\\n', contents)
            contents = [content.strip() for content in contents if content.strip()]
            i = 0
            merged_contents = []
            while i < len(contents):
                if re.match(r'。', contents[i]):
                    merged_contents.append(contents[i] + ' ' + contents[i+1])
                    i += 2
                else:
                    merged_contents.append(contents[i])
                    i += 1
                    
            # 对文档进行分词        
            tokenized_documents = [tokenize(doc) for doc in merged_contents]
            
            # 对查询进行分词
            tokenized_query = tokenize(question)
            
            # 将文档和查询分别转化为TF-IDF向量
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(tokenized_documents)
            
            # 查询向量化
            query_vec = vectorizer.transform([tokenized_query])
            
            # 计算查询向量与文档向量之间的余弦相似度
            cosine_similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
            
            # 输出每个文档的相似度分数
            for idx, score in enumerate(cosine_similarities):
                
                similarities.append((score, titles, book_names, book_numbers, merged_contents[idx]))

    all_sentence_combinations = sorted(similarities, key=lambda x: x[0], reverse=True)                

    # 修正对top_content的选择，需要从all_sentence_combinations中取值
    top_content = [line for _, _, _, _, line in all_sentence_combinations[:10]]
    top_title = [title for _, title, _, _, _ in all_sentence_combinations[:10]]
    top_book = [book_name for _, _, book_name, _, _ in all_sentence_combinations[:10]]
    top_number = [book_number for _, _, _, book_number, _ in all_sentence_combinations[:10]]

    pattern = r'表\d+\.\d+\.\d'

    for picture_name in top_content:
        if re.findall(pattern, picture_name):
            matches_picture.append(re.findall(pattern, picture_name))

        else:
            matches_picture.append(False)


    # 返回修正后的内容
    content = zip(top_content, top_book, top_title, top_number)
    return content, matches_picture

