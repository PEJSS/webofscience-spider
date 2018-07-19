from urllib.request import urlopen
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
from tqdm import tqdm
import csv
import os

def getLink(url,tag,attribute):
    html = urlopen(url)
    bso = BeautifulSoup(html.read(),"html.parser")
    temp = bso.find_all(tag,class_=attribute)
    return temp

def getRefInfo(item):
    raw_authors = item.find_all('span',class_='label')
    author = None
    for child in raw_authors:
        if 'By:' in child.string:
            author = child.parent.contents[2]
        elif "Group Author(s):" in child.string:
            author = child.parent.contents[2]
        elif "Edited by:" in child.string:
            author = child.parent.contents[2]
    if author is None:
        author = "不可用"
        print(4 * '-')
        print("author not found!")
        print(item)
        print(4 * '-')
    if item.find('span',class_='reference-title') == None:
        return '标题不可用' + ' 作者：' + author + ';\r\n'
    else:
        return item.find('span',class_='reference-title').value.string + ' 作者：' + author + ';\r\n'

def getRefPage(input):
    # 30 papers per page
    Url, i = input[0], input[1]
    referlink = Url + str(i)
    html2 = urlopen(referlink)
    bso2 = BeautifulSoup(html2.read(),"html.parser")
    raw_refers = bso2.find_all('div',class_='search-results-item')
    workers = 1
    try:
        refers = ThreadPool(workers).map(getRefInfo, raw_refers)
    except:
        refers = [getRefInfo(item) for item in raw_refers]
    refer = ''.join(refers)
    return refer

def getInfo(url,PassageName, Info, Used, Summary, AuthorInfo, ReferInfo):
    html = urlopen(url)
    bso = BeautifulSoup(html.read(),"html.parser")

    passagename = bso.find(PassageName[0],class_=PassageName[1]).value.string
    info = bso.find_all(Info[0],class_=Info[1])
    usedtimes = bso.find(Used[0],class_=Used[1]).string
    authorinfo = bso.find_all(AuthorInfo[0],class_=AuthorInfo[1])
    SU = bso.find_all(Summary[0],class_=Summary[1])
    referinfo = bso.find(ReferInfo[0],attrs={'title':ReferInfo[1]})
    if referinfo is None:
        print(bso)
        return None
    else:
        link = 'http://apps.webofknowledge.com'+referinfo['href']

    # Summary Filtering
    SU = [item for item in SU if item.string == 'Abstract']
    if len(SU) == 0:
        summary = "None"
    else:
        summary = SU[0].parent.find('p', class_='FR_field').contents[0]

    # Info Filtering
    for item in info:
        if item.string == 'By:':
            authorname = item.next_sibling.string
        if item.string == 'Published:':
            publishdate = item.parent.contents[2]
        if item.string == 'KeyWords Plus:':
            keywords = ''
            for child in item.next_siblings:
                keywords += child.string + '\r\n'
        if item.string == 'E-mail Addresses:':
            email = item.next_sibling.string
    
    # AuthorInfo Filtering
    address = ''
    for item in authorinfo:
        if item.a != None:
            address += item.a.string +'\r\n'

    # Reference Fetching
    # Find Reference Webpages as html1
    html1 = urlopen(link)
    bso1 = BeautifulSoup(html1.read(),"html.parser")
    N = bso1.find('span',id='pageCount.top').string
    N = int(N)
    refer = ''
    Url = bso1.find('form',id='summary_records_form')['paging_url']

    # Get Webpages with Page Altering
    workers = 1
    inputs = [(Url, x) for x in range(1, N+1)]
    try:
        refers = ThreadPool(workers).map(getRefPage, inputs)
    except:
        refers = [getRefPage(input) for input in inputs]
    refer = ''.join(refers)

    return [passagename, authorname,publishdate,usedtimes,keywords,summary,address,email,refer]

def getPage(input):
    start_url, pagenum = input[0], input[1]
    workers = 10
    journal=getLink(start_url + str(), "a","smallV110 snowplow-full-record")
    try:
        results = ThreadPool(workers).map(getArticle, journal)
    except:
        results = [getArticle(item) for item in journal]
    results = filter(None, results)
    return results
    print(10 * '-')
    print("results:")
    print(results)
    print(10 * '-')

def getArticle(item):
    arti='http://apps.webofknowledge.com'+item['href']
    b=getInfo(url=arti,
            PassageName=['div','title'],
            Info=['span','FR_label'],
            Used=['span','large-number'],
            Summary=['div','title3'],
            AuthorInfo=['td','fr_address_row2'],
            ReferInfo=['a',"View this record's bibliography"])
    return b
       
def main():
    record_filename = "record"
    if os.path.exists(record_filename):
        with open(record_filename) as record:
            content = record.read()
            if content == '':
                next_page = 2
            else:
                next_page = int(content)
    else:
        next_page = 2
    # Initialize csv file
    data_filename = 'data.csv'
    if not os.path.exists(data_filename):
        with open(data_filename,'w',newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['文章标题','作者名字','出版年','被引频次',\
            '关键词','摘要','作者地址','电子邮件','参考文献'])

    # start_url = "http://apps.webofknowledge.com/summary.do?product=WOS&parentProduct=WOS&search_mode=GeneralSearch&parentQid=&qid=2&SID=8Ev2lmRWkPOJK5J8HhG&&update_back2search_link_param=yes&page="
    start_url = "http://apps.webofknowledge.com/summary.do?product=UA&parentProduct=UA&search_mode=GeneralSearch&parentQid=&qid=402&SID=5EtvIBjhu6XJQX4QAaz&&update_back2search_link_param=yes&page="
    workers = 1
    for i in tqdm(range(next_page, int((391 + workers - 1) / workers))):
        inputs = [(start_url, i * workers + x) for x in range(workers)]
        try:
            results_buffer = ThreadPool(workers).map(getPage,inputs)
        except:
            results_buffer = [getPage(input) for input in inputs]
        for results in results_buffer:
            with open(data_filename,'a',newline='') as csvfile:
                writer = csv.writer(csvfile)
                for b in results:
                    writer.writerow(b)
        next_page += 1
        with open(record_filename, 'w') as record:
            record.write(str(next_page))

if __name__ == '__main__':
    main()