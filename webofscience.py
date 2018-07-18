from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv

def getHTML(url):
    return urlopen(url)

def getLink(html,tag,attribute):
    bso = BeautifulSoup(html.read(),"lxml")
    temp = bso.find_all(tag,class_=attribute)
    return temp

def getInfo(url,PassageName=[],Info=[],Used=[],Summary=[],AuthorInfo=[]):#,ReferInfo=[]):
    html = urlopen(url)
    bso = BeautifulSoup(html.read(),"lxml")
    passagename = bso.find(PassageName[0],class_=PassageName[1]).value.string
    info = bso.find_all(Info[0],class_=Info[1])
    usedtimes= bso.find(Used[0],class_=Used[1]).string
    authorinfo = bso.find_all(AuthorInfo[0],class_=AuthorInfo[1])
    SU = bso.find_all(Summary[0],class_=Summary[1])
    for item in SU:
        if item.string == 'Abstract':
            summary = item.parent.find("p", class_="FR_field").string)
        else:
            continue
    for item in info:
        if item.string == 'By:':
            authorname = item.next_sibling.string
        #if item.string == 'Published:':
            #publishdate = item.parent.string
        if item.string == 'KeyWords Plus:':
            keywords = ''
            for child in item.next_siblings:
                keywords += child.string
        else:
            continue
        #if item.string == 'E-mail Addresses:':
            #email = item.next_sibling.string
    address = ''
    for item in authorinfo:
        if item.a != None:
            address += item.a.string
    return [passagename,authorname,usedtimes,keywords, summary, address]


def main(i):    
    # journal=getLink("http://apps.webofknowledge.com/summary.do?product=WOS&parentProduct=WOS&search_mode=GeneralSearch&parentQid=&qid=2&SID=8Ev2lmRWkPOJK5J8HhG&&update_back2search_link_param=yes&page=" + str(i), "a","smallV110 snowplow-full-record")
    search_url = "http://apps.webofknowledge.com/Search.do?product=UA&SID=5EUqZRE9OnObDuWiVnH&search_mode=GeneralSearch&prID=c49ab890-a43a-4252-a392-03cc8d8fbeae"
    my_html = getHTML(search_url)
    # open('jss.html', 'w').write(my_html)
    journal=getLink(my_html, "a", "smallV110 snowplow-full-record")

    for item in journal:
        arti='http://apps.webofknowledge.com'+item['href']
        b=getInfo(url=arti,
                  PassageName=['div','title'],
                  Info=['span','FR_label'],
                  Used=['span','large-number'],
                  Summary=['div', 'title3'], 
                  AuthorInfo=['td','fr_address_row2'])
                  #ReferInfo=['a',"View this record's bibliography"])
        with open('data.csv','a',newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(b)

with open('data.csv','w',newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['文章标题','作者名字','被引频次','关键词', '摘要', '作者地址'])

main(0)
print("success!")

# for i in range(1,391):
    # main(i)