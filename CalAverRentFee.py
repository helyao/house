# -*- coding: utf-8 -*-
# Calculate Average Rent Fee with the same Zipcode
# @Version    :   1.0
# @Author     :   Helyao
# * 2018-05-16    Init
import os
import time
import random
import pymysql
import requests
from bs4 import BeautifulSoup
from configparser import ConfigParser

CACHE_SALE = r'./cache/sale'
CACHE_RENT = r'./cache/rent'
CACHE_LIST = r'./cache/list'

CRAWLER = True

BASE_URL = 'https://www.realtor.com'

user_agent_list = [
    "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_2 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8H7 Safari/6533.18.5",
    "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_2 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8H7 Safari/6533.18.5",
    "MQQBrowser/25 (Linux; U; 2.3.3; zh-cn; HTC Desire S Build/GRI40;480*800)",
    "Mozilla/5.0 (Linux; U; Android 2.3.3; zh-cn; HTC_DesireS_S510e Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (SymbianOS/9.3; U; Series60/3.2 NokiaE75-1 /110.48.125 Profile/MIDP-2.1 Configuration/CLDC-1.1 ) AppleWebKit/413 (KHTML, like Gecko) Safari/413",
    "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Mobile/8J2",
    "Mozilla/5.0 (Windows NT 5.2) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.122 Safari/534.30",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.202 Safari/535.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/534.51.22 (KHTML, like Gecko) Version/5.1.1 Safari/534.51.22",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A5313e Safari/7534.48.3",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A5313e Safari/7534.48.3",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A5313e Safari/7534.48.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.202 Safari/535.1",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; SAMSUNG; OMNIA7)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; XBLWP7; ZuneWP7)",
    "Mozilla/5.0 (Windows NT 5.2) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.122 Safari/534.30",
    "Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET4.0E; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET4.0E; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)",
    "Mozilla/4.0 (compatible; MSIE 60; Windows NT 5.1; SV1; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Opera/9.80 (Windows NT 5.1; U; zh-cn) Presto/2.9.168 Version/11.50",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022; .NET4.0E; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727; TheWorld)"
]

def getAgentRandom():
    global user_agent_list
    return user_agent_list[random.randint(0, (len(user_agent_list) - 1))]

# Download url page
def download(url, name, agent=None, force=False):
    if force == False:
        if os.path.exists(name):
            return True
    if agent == None:
        agent = getAgentRandom()
    headers = {'User-agent': agent}
    res = requests.get(url, headers=headers, allow_redirects=False)
    print(url)
    print(res.status_code)
    if res.status_code == 200:
        html = res.content.decode('utf-8')
        try:
            with open(name, 'w', encoding='utf-8') as file:
                file.write(html)
        except Exception as ex:
            print(ex)
            return False
    else:
        return False
    return True

# Explain detail information for sale
def getSaleInfoDetail(uid):
    res = {'uid': uid}
    try:
        with open('{}/{}.html'.format(CACHE_SALE, uid), 'r', encoding='utf-8') as file:
            html = file.read()
            soup = BeautifulSoup(html, 'lxml')
            div1 = soup.select_one('#ldp-sticky-bar-js-save')
            info_lis = div1.select_one('.property-meta').select('li')
            for li in info_lis:
                key = li.attrs['data-label'].replace('property-meta-', '')
                value = int(li.select_one('.data-value').text.strip().replace(',', ''))
                res[key] = value
            price_lis = div1('li')
            for li in price_lis:
                if '$' in li.text.strip():
                    res['price'] = int(li.text.strip().replace('$', '').replace(',', '').replace('Est.', ''))
            div2 = soup.select_one('#key-fact-carousel')
            info_2_lis = div2.select_one('.owl-carousel').select('li')
            for li in info_2_lis:
                key = li.select_one('div').text.strip().lower()
                value = li.select_one('.key-fact-data').text.strip()
                if key == 'price/sq ft':
                    key = 'average'
                elif 'realtor.com' in key:
                    key = 'hang'
                res[key] = value
        return res
    except Exception as ex:
        print(ex)
        return False

# Get max page of rent list
def getMaxPageOfRentList(zipcode):
    try:
        with open('./{}/{}.html'.format(CACHE_LIST, zipcode), 'r', encoding='utf-8') as file:
            html = file.read()
            soup = BeautifulSoup(html, 'lxml')
            pages = soup.select_one('#ResultsPerPageBottom').select('.page')
            max = int(pages[-1].text.strip())
            return max
    except Exception as ex:
        print(ex)
        return 0

# Get rent urls
def getRentUrls(name):
    res = []
    with open(name, 'r', encoding='utf-8') as file:
        html = file.read()
        soup = BeautifulSoup(html, 'lxml')
        lis = soup.select_one('#srp-list').select('.srp-item')
        count = 0
        for li in lis:
            if 'data-url' in li.attrs.keys():
                link = li.attrs['data-url']
                # print(link)
                count += 1
                res.append(BASE_URL + link)
        print('count = {}'.format(count))
    return res

# Get rent list
def getRentList(zipcode):
    res = {'zipcode': zipcode, 'list': []}
    max = getMaxPageOfRentList(zipcode)
    for i in range(max):
        page = i + 1
        print('page = {}/{}'.format(page, max))
        time.sleep(3 + int(3 * random.random()))
        if page > 1:
            url = 'https://www.realtor.com/apartments/{}/pg-{}'.format(zipcode, page)
            if download(url, './{}/{}-{}.html'.format(CACHE_LIST, zipcode, page), force=CRAWLER):
                list = getRentUrls('./{}/{}-{}.html'.format(CACHE_LIST, zipcode, page))
                if list:
                    res['list'].extend(list)
        else:
            list = getRentUrls('./{}/{}.html'.format(CACHE_LIST, zipcode))
            if list:
                res['list'].extend(list)
    return res

# Explain detail information for rent
def getRentInfoDetail(uid):
    pass

if __name__ == '__main__':
    # Step1. Get config parameters
    conf = ConfigParser()
    conf.read('config.ini')
    # [mysql]
    mysql_host = conf.get('mysql', 'host')
    mysql_port = int(conf.get('mysql', 'port'))
    mysql_username = conf.get('mysql', 'username')
    mysql_password = conf.get('mysql', 'password')
    mysql_db = conf.get('mysql', 'db')
    mysql_charset = conf.get('mysql', 'charset')
    # [realtor]
    realtor_sample = conf.get('realtor', 'sample')

    # Step2. Get the sample information
    conn = pymysql.connect(
        host=mysql_host, port=mysql_port,
        user=mysql_username, passwd=mysql_password,
        db=mysql_db, charset=mysql_charset
    )
    cursor = conn.cursor()
    sql = '''
        select url, uid, zipcode from record where uid = '{}'
        '''.format(realtor_sample)
    cursor.execute(sql)
    item = cursor.fetchone()
    sample_base_url = item[0]
    sample_zipcode = item[2]
    print("url = {}".format(sample_base_url))
    print("sample = {}".format(realtor_sample))
    print("zipcode = {}".format(sample_zipcode))

    # Step3. Cache the sample detail page
    if download(sample_base_url, './{}/{}.html'.format(CACHE_SALE, realtor_sample), force=CRAWLER):
        res = getSaleInfoDetail(realtor_sample)
        if res:
            print('result = {}'.format(res))
    time.sleep(3 + int(3 * random.random()))

    # Step4. Cache all the rent detail page with the same zipcode
    if download('https://www.realtor.com/apartments/{}'.format(sample_zipcode), './{}/{}.html'.format(CACHE_LIST, sample_zipcode), force=CRAWLER):
        res = getRentList(sample_zipcode)
        if res:
            print('result = {}'.format(res))

    # Step5: Get the information of all the rent pages
