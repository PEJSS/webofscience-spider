from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
def getLink(url,tag,attribute):
    html = urlopen(url)
    bso = BeautifulSoup(html.read(),"lxml")
    temp = bso.find_all(tag,class_=attribute)
    return temp

def getInfo(url,PassageName=[],Info=[],Used=[],Summary=[],AuthorInfo=[],ReferInfo=[]):
    html = urlopen(url)
    bso = BeautifulSoup(html.read(),"lxml")
    passagename = bso.find(PassageName[0],class_=PassageName[1]).value.string
    info = bso.find_all(Info[0],class_=Info[1])
    usedtimes = bso.find(Used[0],class_=Used[1]).string
    authorinfo = bso.find_all(AuthorInfo[0],class_=AuthorInfo[1])
    SU = bso.find_all(Summary[0],class_=Summary[1])
    referinfo = bso.find(ReferInfo[0],attrs={'title':ReferInfo[1]})
    link = 'http://apps.webofknowledge.com'+referinfo['href']
    for item in SU:
        if item.string == 'Abstract':
            summary = item.parent.find('p',class_='FR_field').string
    for item in info:
        if item.string == 'By:':
            authorname = item.next_sibling.string
        if item.string == 'Published:':
            publishdate = item.parent.contents[2]
        if item.string == 'KeyWords Plus:':
            keywords = ''
            for child in item.next_siblings:
                keywords += child.string
        if item.string == 'E-mail Addresses:':
            email = item.next_sibling.string
    address = ''
    for item in authorinfo:
        if item.a != None:
            address += item.a.string
    html1 = urlopen(link)
    bso1 = BeautifulSoup(html1.read(),"lxml")
    N = bso1.find('span',id='pageCount.top').string
    N = int(N)
    refer = ''
    for i in range(1,N+1):
        referlink = "http://apps.webofknowledge.com/summary.do?product=WOS&parentProduct=WOS&search_mode=CitedRefList&parentQid=1&qid=6&SID=6CgFCpcFxmzntOHn1tw&&page=" + str(i)
        html2 = urlopen(referlink)
        bso2 = BeautifulSoup(html2.read(),"lxml")
        refers = bso2.find_all('div',class_='search-results-item')
        for item in refers:
            print(item)
            print(item.find('span',class_='reference-title'))
            authors = item.find_all('span',class_='label')
            authors = [x.parent.contents[2] for x in authors if x.string == '作者：']
            # for child in authors:
                # if child.string == '作者: ':
                    # author = child.parent.contents[2]
            if len(authors) == 0:
                raise ValueError("No authors found!")
            refer += item.find('span',class_='reference-title').value.string + '作者：' + author + ';'
    return [passagename,authorname,publishdate,usedtimes,keywords,summary,address,email,refer]

with open('data.csv','w',newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['文章标题','作者名字','出版年','被引频次','关键词','摘要','作者地址','电子邮件','参考文献'])
for i in range(1,391):
    journal=getLink("http://apps.webofknowledge.com/summary.do?product=WOS&parentProduct=WOS&search_mode=GeneralSearch&parentQid=&qid=2&SID=8Ev2lmRWkPOJK5J8HhG&&update_back2search_link_param=yes&page=" + str(i), "a","smallV110 snowplow-full-record")
    for item in journal:
        arti='http://apps.webofknowledge.com'+item['href']
        b=getInfo(url=arti,
                  PassageName=['div','title'],
                  Info=['span','FR_label'],
                  Used=['span','large-number'],
                  Summary=['div','title3'],
                  AuthorInfo=['td','fr_address_row2'],
                  ReferInfo=['a',"View this record's bibliography"])
        with open('data.csv','a',newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(b)