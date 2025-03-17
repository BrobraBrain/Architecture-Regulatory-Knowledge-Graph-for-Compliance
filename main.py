import pika, sys, os
import zerorpc
from model_utils import tokenizer, model
from keyword_extraction import extract_keywords, function_decision, translate, question_check
from content_extraction import extract_content
from similarity import similarity_find
from image_utils import picture_store
from upload_handler import upload_file_keyword
from file_utils import OssOperate
import json
import threading

# 定义下载的函数
oss_obj = OssOperate("dev")


# 初始化一个全局的线程锁
lock = threading.Lock()

#连接robbitmq，进行输入问题捕捉
credentials =pika.PlainCredentials(username='###############',password='###############')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='###############', port=15672,credentials=credentials))

#去掉相同的图片
def remove_duplicates(pictures_data, pictures_name, pictures_number):
    seen = list()
    unique_pictures_data = []
    unique_pictures_name = []
    unique_pictures_number = []

    for data, name, number in zip(pictures_data, pictures_name, pictures_number):
        if data not in seen:
            seen.append(data)
            unique_pictures_data.append(data)
            unique_pictures_name.append(name)
            unique_pictures_number.append(number)

    return unique_pictures_data, unique_pictures_name, unique_pictures_number


#运算问题，生成回答的功能
def predict(question, file_upload, max_length, top_p, temperature, history=None):
    if history is None:
        history = []
        
    if question:   
        #判断是生成图片还是文字
        decision = function_decision(question)
        #限制每次只能运行一个传输
        print(decision)
        if decision == "picture":
            with lock:
                try:
                # 判断是否图片生成
            
                    # 基于问题生成prompt
                    pic_request = translate(question)
                    print(pic_request)
                    print("发送了")
                    # 这里输入图片处理框架

                    print("con rpc")
                    client = zerorpc.Client(heartbeat=120,timeout=60)
                    client.connect("###############")
                    print('call func')
                    answer = client.txt_g_img(pic_request)

                    print(answer)
                    regulation_mark = "False"
                
                except Exception as e:
                    print(f"Error: {e}")
                finally:
                    client.close()
            
        # 文字输出
        if decision == "text":
            
            # 判断是否上传文件
            if file_upload:
                print("文件在分析")
                keywords_reference = upload_file_keyword(file_upload, question)
                prompt = f"""请基于{keywords_reference}简洁回答问题：{question}"""
                
                all_false = False
                #大模型回答
                response, history = model.chat(tokenizer, prompt, history=None, max_length=max_length)
                answer = response
                regulation_mark = "False"
                
            
            #如果没有文件上传    
            else:
                questions_check = question_check(question)
                ############ 如果输入的问题和规范相关
                if len(questions_check) > 0:
                    # 基于规范的符号判别
                    input_keywords = extract_keywords(question)
                    regulation_mark = "True"
                    raw_content = extract_content(input_keywords)
                    all_content, matches_picture = similarity_find(question, raw_content)
                    content = []
                    print_content = ""
                    for item1, item2, item3, item4 in all_content:
                        book_number = f"规范编号：{item4}"
                        book_name = f"规范名称：{item2}"
                        section_title = f"章节名称：{item3}"
                        book_content = f"规范内容：{item1}"
                        content.append(item1)
                        print_content += f"\n{book_number}\n{book_name}\n{section_title}\n{book_content}\n"
                    content = "".join(content)
                    prompt = f"""请基于{content}简洁回答问题：{question}"""
                    
                    #返回规范图片
                    
                    all_false = any(matches_picture)
                    print(matches_picture)
                    print(all_false)
                    if all_false:
                        picture_data, picture_name, picture_number = picture_store(question)

                        response, history = model.chat(tokenizer, prompt, history=None, max_length=max_length)
                        reference = "参考规范：" + print_content
                        response_text = "根据建筑规范回答：" + response
                        ################
                        # 返回基于规范回答及图片的回答
                        answer = reference, response_text, picture_data, picture_name, picture_number
                    else:
                        response, history = model.chat(tokenizer, prompt, history=None, max_length=max_length)
                        reference = "参考规范：" + print_content
                        response_text = "根据建筑规范回答：" + response
                        ################
                        # 返回基于规范回答(无图片)
                        answer = reference, response_text, all_false, all_false, all_false
                        
                # 如果输入的问题和规范无关
                else:
                    response, history = model.chat(tokenizer, question, history=None, max_length=max_length)
                    answer = response
                    decision = "text"
                    regulation_mark = "False"
    return answer, decision, regulation_mark

#调用回答
def handle_answer(input_question_words, file_upload, max_length=100000, top_p=0.7, temperature=0.95):
    
    #调用语言模型函数
    answer, decision, regulation_mark = predict(input_question_words, file_upload, max_length, top_p, temperature)
    data = {
                    "text":"",
                    "image": []
                    }

    if decision == "picture":
        
        for image_g in answer:            
            data['image'].append({"pic_uri": image_g})
            
        #判断是否有上传文件
        
    elif decision == "text":
        
        #参考规范的回答
        if regulation_mark == "True":
            #如果想查看参考规范
            #reference, response_text, pictures_data, pictures_name, pictures_number = answer
            #data['text'] = f"{reference} \n \n {response_text} \n"
            _, response_text, pictures_data, pictures_name, pictures_number = answer
            data['text'] = f"{response_text}"
            
            #有图片的规范回答 
            if pictures_data:
                for pic_data, pic_name, pic_num in zip(pictures_data, pictures_name, pictures_number):
                    data['image'].append({
                        "pic_num": pic_num,
                        "pic_name": pic_name,
                        "pic_uri": pic_data
                    })

            
            #没有图片的规范回答            
            else:                
                data['text'] = response_text
                
           
        #返回不参考规范的回答
        else:
            data['text'] = answer
            print(data['text'])
    return json.dumps(data, ensure_ascii=False)

#调用函数 启动！！！
def main():
    #连接channel
    channel = connection.channel()
    #创建接收问题的queue
    channel.queue_declare(queue='hello')
    
    
    #发布回答回channel
    def callback(ch, method, properties, body):
        #给每一个接受问题创立单独一个返回的queue
        print(body)
        bodystr = body.decode()
        jsondata = json.loads(bodystr)
        send_queue = jsondata.get("queue")
        #创立每一个接受问题返回decisiondecision的queue
        channel.queue_declare(queue=send_queue)
        
        #提取其中的content
        content = jsondata.get("input")
        
        #提取上传文件地址
        #原本的地址
        oss_uri = jsondata.get("file")
        print(oss_uri)
        #将文件下载到的地址
        if oss_uri:
            save_path = r"/home/fength/fllm/Download"
            file_location = oss_obj.download_file(oss_uri[0], save_path)
            print(oss_uri[0])
            print(file_location)

        else:
            file_location = False
        
        #处理问题，返回基于问题的回答
        giveback = handle_answer(content, file_location)
        channel.basic_publish(exchange='', routing_key=send_queue, body=giveback)
        

    #接受问题consuming开始
    channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)








        






