import requests
import re

def main():
    home = 'http://www.webofknowledge.com/'
    s = requests.get(home)
    sid = re.findall(r'SID=\w+&', s.url)[0].replace('SID=', '').replace('&', '')
    PublisherName = "american economic review"

    headers = {
            'Origin': 'https://apps.webofknowledge.com',
            'Referer': 'https://apps.webofknowledge.com/UA_GeneralSearch_input.do?product=UA&search_mode=GeneralSearch&SID=R1ZsJrXOFAcTqsL6uqh&preferencesSaved=',
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36",
            'Content-Type': 'application/x-www-form-urlencoded'
    }

    form_data = {
        'fieldCount': 1,
        'action': 'search',
        'product': 'WOS',
        'search_mode': 'GeneralSearch',
        'SID': sid,
        'max_field_count': 25,
        'formUpdated': 'true',
        'value(input1)': PublisherName,
        'value(select1)': 'SO',
        'value(hidInput1)': '',
        'limitStatus': 'collapsed',
        'ss_lemmatization': 'On',
        'ss_spellchecking': 'Suggest',
        'SinceLastVisit_UTC': '',
        'SinceLastVisit_DATE': '',
        'period': 'Range Selection',
        'range': 'ALL',
        'startYear': '1900',
        'endYear': '2018',
        'update_back2search_link_param': 'yes',
        'ssStatus': 'display:none',
        'ss_showsuggestions': 'ON',
        'ss_query_language': 'auto',
        'ss_numDefaultGeneralSearchFields': 1,
        'rs_sort_by': 'PY.D;LD.D;SO.A;VL.D;PG.A;AU.A'
    }

    form_data2 = {
        'product': 'WOS',
        'prev_search_mode': 'CombineSearches',
        'search_mode': 'CombineSearches',
        'SID': sid,
        'action': 'remove',
        'goToPageLoc': 'SearchHistoryTableBanner',
        'currUrl': 'https://apps.webofknowledge.com/WOS_CombineSearches_input.do?SID=' + sid + '&product=WOS&search_mode=CombineSearches',
        'x': 48,
        'y': 9,
        'dSet': 1
    }

    root_url = 'https://apps.webofknowledge.com/WOS_GeneralSearch.do'
    session = requests.Session()
    respond = session.post(root_url, data=form_data, headers=headers)
    respond.encoding = respond.apparent_encoding
    html = respond.text
    print(html)
    with open('post.html', 'w') as html_file:
        html_file.write(html.encode('utf8'))

if __name__ == "__main__":
    main()