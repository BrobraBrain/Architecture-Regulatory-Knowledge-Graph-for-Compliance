import requests
import time
from lxml import etree

#构造url列表
urls = ['http://www.jianbiaoku.com/webarbs/list/117/{}.shtml'.format(page) for page in range(1, 43)]

#设置headers请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
}

for index, url in enumerate(urls):
    #设置休眠时间，防止被识别为爬虫
    time.sleep(1)
    response = requests.get(url=url, headers=headers)
    response.encoding = 'utf-8'
    content = response.text
    
    #利用xpath定位获取每页的所有规范的<div>标签
    html = etree.HTML(content)
    items = html.xpath('//div[@class="book_list_data"]/div[@class="book_item"]')
    print('开始爬取第{}页'.format(index+1))
    
    #遍历获取每个<div>标签下的规范名称（bz_name）、规范编号（bz_id）、更新时间（bz_time）
    for item in items:
        #设置异常处理，提高代码的容错性
        try:
            bz_name = item.xpath('./span[@class="book_name"]/a/text()')[0]
            bz_id = item.xpath('./span[@class="book_version"]/text()')[0]
            bz_time = item.xpath('./span[@class="book_date"]/text()')[0]
            #将获取的内容保存到“国家规范-建筑专业.csv”文件下
            with open('国家规范-建筑专业2.txt', 'a', encoding='GBK') as f:
                f.write(bz_name+','+bz_id+','+bz_time+'\n')
            print(bz_name, bz_id, bz_time)
        except IndexError:
            print('数据异常')
            pass
        continue