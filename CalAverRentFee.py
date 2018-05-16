# -*- coding: utf-8 -*-
# Calculate Average Rent Fee with the same Zipcode
# @Version    :   1.0
# @Author     :   Helyao
# * 2018-05-16    Init
import os
import pymysql
import requests
from bs4 import BeautifulSoup
from configparser import ConfigParser

CACHE_SALE = r'./cache/sale'
CACHE_RENT = r'./cache/rent'

# Download url page
def download(url, uid, path):
    if os.path.exists('{}/{}.html'.format(path, uid)):
        return True
    res = requests.get(url)
    if (res.status_code == 200):
        html = res.content.decode('utf-8')
        try:
            with open('{}/{}.html'.format(path, uid), 'w', encoding='utf-8') as file:
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
            div = soup.select_one('#ldp-sticky-bar-js-save')
            info_lis = div.select_one('.property-meta').select('li')
            for li in info_lis:
                key = li.attrs['data-label'].replace('property-meta-', '')
                value = int(li.select_one('.data-value').text.strip().replace(',', ''))
                res[key] = value
            price_lis = div('li')
            for li in price_lis:
                if '$' in li.text.strip():
                    res['price'] = int(li.text.strip().replace('$', '').replace(',', ''))
        return res
    except Exception as ex:
        print(ex)
        return False

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
    realtor_demo = conf.get('realtor', 'sample')

    # Step2. Get the sample information
    conn = pymysql.connect(
        host=mysql_host, port=mysql_port,
        user=mysql_username, passwd=mysql_password,
        db=mysql_db, charset=mysql_charset
    )
    cursor = conn.cursor()
    sql = '''
        select url, uid, zipcode from record where uid = '{}'
        '''.format(realtor_demo)
    cursor.execute(sql)
    item = cursor.fetchone()
    sample_base_url = item[0]
    sample_zipcode = item[2]

    # Step3. Cache the sample detail page
    if download(sample_base_url, realtor_demo, CACHE_SALE):
        res = getSaleInfoDetail(realtor_demo)
        if res:
            print('result = {}'.format(res))

    # Step4. Cache all the rent detail page with the same zipcode
