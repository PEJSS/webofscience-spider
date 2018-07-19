from urllib.request import urlopen
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
from tqdm import tqdm
import csv

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
    workers = 5
    pool = ThreadPool(workers)
    refers = pool.map(getRefInfo, raw_refers)
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
    workers = N
    pool = ThreadPool(workers)
    inputs = [(Url, x) for x in range(1, N+1)]
    refers = pool.map(getRefPage, inputs)
    refer = ''.join(refers)

    return [passagename, authorname,publishdate,usedtimes,keywords,summary,address,email,refer]

def getPage(start_url, pagenum, workers = 10):
    journal=getLink(start_url + str(), "a","smallV110 snowplow-full-record")
    pool = ThreadPool(workers)
    results = pool.map(getArticle, journal)
    results = (None, results)
    print(10 * '-')
    print("results:")
    print(results)
    print(10 * '-')
    for b in results:
        with open('data.csv','a',newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(b)

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
    # Initialize csv file
    with open('data.csv','w',newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['文章标题','作者名字','出版年','被引频次',\
        '关键词','摘要','作者地址','电子邮件','参考文献'])

    # start_url = "http://apps.webofknowledge.com/summary.do?product=WOS&parentProduct=WOS&search_mode=GeneralSearch&parentQid=&qid=2&SID=8Ev2lmRWkPOJK5J8HhG&&update_back2search_link_param=yes&page="
    start_url = "http://apps.webofknowledge.com/summary.do?product=UA&parentProduct=UA&search_mode=GeneralSearch&parentQid=&qid=1&SID=5EtvIBjhu6XJQX4QAaz&&update_back2search_link_param=yes&page="
    for i in tqdm(range(2, 391)):
        #try:
            #getPage(start_url, i)
        #except Exception as e:
            #print(e)
        getPage(start_url, i)

if __name__ == '__main__':
    main()