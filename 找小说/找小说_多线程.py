# -*- codeing: utf-8 -*-
'''
@File    :   找小说_多线程.py
@Time    :   2020/05/24 21:44:25
@Author  :   sorrowfeng 
@Version :   1.0
@Contact :   1399600304@qq.com
@WebSite :   https://sorrowfeng.github.io
'''

# here put the import lib

import os
import threading
import time

import requests
from lxml import etree

search_url = "http://www.xbiquge.la/modules/article/waps.php?searchkey="
all_url = "http://www.xbiquge.la/xiaoshuodaquan/"


# threadLock = threading.Lock()
threads = []



# 将两个列表对应组和成一个新的字典
def list_dic(list1,list2):
    '''
    two lists merge a dict,a list as key,other list as value
    :param list1:key
    :param list2:value
    :return:dict
    '''
    dic = dict(map(lambda x,y:[x,y], list1,list2)) # lambda是匿名函数, 冒号前为参数, 后面为返回值, 即传入x, y, 返回[x,y]
    return dic                                     # map函数, 第一个参数为函数名, 后面为参数, 返回返回一个将 function 应用于 iterable 中每一项并输出其结果的迭代器。


# thread类
class myThread (threading.Thread):
    def __init__(self, zhang_name, zhang_url, shu_name):
        threading.Thread.__init__(self)
        self.zhang_name = zhang_name
        self.zhang_url = zhang_url
        self.shu_name = shu_name
    def run(self):
        # 获取锁，用于线程同步
        # threadLock.acquire()
        spider.requests_data(self.zhang_name, self.zhang_url, self.shu_name)
        # 释放锁，开启下一个线程
        # threadLock.release()



class Spider:
    word = ''   # 搜索字段
    file_name = ''  # 文件名
    download_num = 0    # 下载数

    def __init__(self, word):
        self.word = word    # 初始化参数

    def start_requests(self):
        # 1. 请求网站拿到数据，抽取小说名创建文件夹，抽取小说链接
        start_url = search_url + str(self.word)
 
        # print(start_url)
        response = requests.get(start_url)  # 请求链接
        response.encoding="utf-8"       # 解决了获取到的中文名称乱码的问题
        myhtml = etree.HTML(response.text)  # 解析并返回一个 Element 对象
        
        # 通过xpath定位想要获取的元素
        name_list = myhtml.xpath("//div[@id='content']/form/table[@class='grid']/tr/td[@class='even'][1]/a/text()")
        url_list = myhtml.xpath("//div[@id='content']/form/table[@class='grid']/tr/td[@class='even'][1]/a/@href")
        author_list = myhtml.xpath("//div[@id='content']/form/table[@class='grid']/tr/td[@class='even'][2]/text()")
        # 将两个列表对应组和成一个新的字典name_url_dic
        name_url_dic = list_dic(name_list, url_list)
        name_author_dic = list_dic(name_list, author_list)
        # print(name_url_dic)   

        if not name_url_dic: # 如果字典为空
            print("没有找到此书")
            os.system('pause')
            return

        num = 0 # 序号
        find_dic = {} # 搜索找到的结果, 构成的字典  
        print('\n')
        for name in name_url_dic:
            num += 1
            find_dic[str(num)]=name    # 将找到的结果再放入一个字典内, 方便序号查找
            print(str(num) + '.  ' +  name + ('\t\t作者: ' + str(name_author_dic[name])))
        book_num = input('\n你想下载的是(请输入序号):')
        print('\n\n')
        shu_name = find_dic[book_num]  # 确定书名
        shu_url = name_url_dic.get(shu_name)  # 从字典中找到对应书名的链接      
        print('正在为你下载:'+shu_name+'\n')

        if os.path.exists(shu_name) == False:   # 如果文件夹不存在
            os.mkdir(shu_name)  # 新建文件夹

        self.requests_zhang(shu_name,shu_url)   # 请求每个章节的链接
    


    def requests_zhang(self,shu_name,shu_url):
        # 2. 请求小说拿到数据，抽取章名、文章链接
        response = requests.get(shu_url)
        # 乱码 header显示编码格式是ISO-8859-1 内容的格式是utf-8 需要修改代码格式
        response.encoding='utf-8'
        # print(response.encoding) #没定义编码格式的时候，header显示的编码格式
        # print(response.apparent_encoding) #内容实际采用的编码格式
        # print(response.headers) #查看头标签内容
        html = etree.HTML(response.text)
        zhang_name_list = html.xpath('//div[@id="list"]/dl/dd/a/text()')    # 获取每章的名称
        zhang_url_list =html.xpath('//div[@id="list"]/dl/dd/a/@href')       # 获取每章的链接
        
        self.all_zhang_num = len(zhang_name_list)   # 总章节数

        for zhang_name,zhang_url in zip(zhang_name_list,zhang_url_list):
            thread_num = myThread(zhang_name, zhang_url, shu_name) # 新建新线程对象
            time.sleep(0.015)    # 加入延迟, 否则会漏章节
            thread_num.start()   # 开始线程
            threads.append(thread_num) # 添加线程到线程列表
            time.sleep(0.015)    # 加入延迟, 否则会漏章节

        # 释放所有线程
        for t in threads:
            time.sleep(0.01)
            # print(t)
            t.join()
           
        print('\n下载完成!存放于' + os.getcwd() + ', 共' + str(self.all_zhang_num) + '章' + '\n')
        print('正在准备退出')
        os.system('pause')

    # 请求具体的每章内容
    def requests_data(self,zhang_name,zhang_url,shu_name):
        # 3. 请求文章拿到文章内容，创建文件保存到相应文件夹
        data_url = 'http://www.xbiquge.la'+zhang_url    # 每章的url
        response = requests.get(data_url)
        response.encoding='utf-8'   # 编码
        html = etree.HTML(response.text)

        content = "\n".join(html.xpath('//div[@id="content"]/text()'))  # 将"\n"作为后面返回内容的拼接
        # zhang_name = zhang_name[0:16].split('（')[0] # 将章节名截断为[0:16], 并以'（' 分隔, 作用: 去掉上中下的后缀, (没必要)
        self.download_num += 1   # 已下载章节数

        self.file_name = shu_name + '\\' + zhang_name + '.txt'    # 写入的文件名
        print("正在下载：" + zhang_name + "\t已下载  " + str(round((100*self.download_num/self.all_zhang_num), 2)) + "%")   # round函数: round(a, 2), 保留a的小数点后两位
        with open(self.file_name,"a",encoding='utf-8') as f:      # 使用with语句写入文件, 不管在处理文件过程中是否发生异常, 都能保证 with 语句执行完毕后已经关闭了打开的文件句柄
            f.write('\n\n\n'+str(zhang_name)+'\n\n\n')    # 写入章节名
            f.write(content)    # 写入正文内容

        

if __name__ == '__main__':
    word = input('请输入要下载的书名(或作者):')
    spider = Spider(word)
    spider.start_requests() # 开始爬取
