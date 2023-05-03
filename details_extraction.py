import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import string
from dateutil import parser
import os
import csv
from datetime import datetime
import pytz
from googletrans import Translator
import openpyxl

translator = Translator()

#dic = {'https://finance.yahoo.com/news/wearable-fitness-products-market-size-143400419.html': '20 hours ago', 'https://www.realinstitutoelcano.org/en/analyses/brazil-foreign-policy-strategy-after-the-2022-elections/': 'Jun 1, 2022', 'https://apnews.com/article/caribbean-south-america-buenos-aires-argentina-17d4361a9d612a5a39fce125d8cbb20c': 'Dec 6, 2022'}
def detail_extraction(url,date,country_name):
    df = pd.DataFrame(columns=['url_link','title','published_date','data'])
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(chrome_options=options,service=ChromeService(ChromeDriverManager().install()))
    
    indian_tz1 = pytz.timezone('Asia/Kolkata')
    indian_time1 = datetime.now(indian_tz1)

    try:
        for u in range(len(url)):
            indian_tz = pytz.timezone('Asia/Kolkata')
            indian_time = datetime.now(indian_tz)
            
            pub_date = date[u]
            data = []
            title = ''
            res = ''
            publish_date = ''

            print('url : ',url[u])
            print('scrape time >>> ',indian_time.strftime("%d/%m/%Y %H:%M:%S"))
            driver.get(url[u])
            time.sleep(5)
            elem1 = driver.find_elements(By.TAG_NAME,"h1")
            if len(elem1)>0:
                for elem in elem1:
                    title=elem.text
            else:
                elem3 = driver.find_element(By.TAG_NAME,"h2")
                title=elem.text

            elem2 = driver.find_elements(By.CLASS_NAME,"container")
            if len(elem2)>0:
                for elem in elem2:
                    data.append(translator.translate(elem.text).text)
            else:
                elem4 = driver.find_elements(By.TAG_NAME,'p')
                if len(elem4)>0:
                    for elem in elem4:
                        data.append(translator.translate(elem.text).text)
                else:
                    elem5 = driver.find_elements(By.TAG_NAME,'span')
                    if len(elem5)>0:
                        for elem in elem5:
                            data.append(translator.translate(elem.text).text)
                    else:
                        elem6 = driver.find_elements(By.CLASS_NAME,'main-container')
                        if len(elem6)>0:
                            for elem in elem6:
                                data.append(translator.translate(elem.text).text)
                        else:
                            elem7 = driver.find_elements(By.TAG_NAME,'main')
                            if len(elem7)>0:
                                for elem in elem7:
                                    data.append(translator.translate(elem.text).text)
                            else:
                                elem8 = driver.find_elements(By.CLASS_NAME,'content')
                                if len(elem8)>0:
                                    for elem in elem8:
                                        data.append(translator.translate(elem.text).text)
                                else:
                                    elem9 = driver.find_elements(By.CLASS_NAME,'main')
                                    if len(elem9)>0:
                                        for elem in elem9:
                                            data.append(translator.translate(elem.text).text)
                                    else:
                                        elemdate11 = driver.find_elements(By.CLASS_NAME,'article-header-blog__date')
                                        if len(elemdate11)>0:
                                            for elem in elemdate11:
                                                date_object = parser.parse(elem.text)
                                        else:
                                            elemdate12 = driver.find_elements(By.CLASS_NAME,'gem-c-metadata__definition')
                                            if len(elemdate12)>0:
                                                for elem in elemdate12:
                                                    date_object = parser.parse(elem.text)
                                            else:
                                                elemdate13 = driver.find_elements(By.CLASS_NAME,'article-header-blog__date')
                                                if len(elemdate13)>0:
                                                    for elem in elemdate13:
                                                        date_object = parser.parse(elem.text)
            
            #print('title : ',head[0])
            listToStr = ' '.join([str(elem) for elem in data])
            res = re.sub(' +', ' ', listToStr)
            #print('data : ',str(res))

            if re.match(r'\d{2} \w{3} \d{4}', pub_date): # format: 25 Oct 2022
                date_obj = re.search(r'(\d{2}) (\w{3}) (\d{4})', pub_date)
                day, month, year = date_obj.groups()
                publish_date = f'{day}/{month_to_number(month)}/{year}'
                print('publish date >>> ',publish_date)
            elif re.match(r'\w{3,} \d{2}, \d{4}', pub_date): # format: Jan 12, 2023
                date_obj = re.search(r'(\w{3,}) (\d{2}), (\d{4})', pub_date)
                month, day, year = date_obj.groups()
                publish_date = f"{day}/{month_to_number(month)}/{year}"
                print('publish date >>> ',publish_date)
            elif re.match(r'\d{1} \w{3} \d{4}', pub_date): # format: 25 Oct 2022
                date_obj = re.search(r'(\d{1}) (\w{3}) (\d{4})', pub_date)
                day, month, year = date_obj.groups()
                publish_date = f'{day}/{month_to_number(month)}/{year}'
                print('publish date >>> ',publish_date)
            elif re.match(r'\d{2} \w{4} \d{4}', pub_date): # format: 25 Oct 2022
                date_obj = re.search(r'(\d{2}) (\w{4}) (\d{4})', pub_date)
                day, month, year = date_obj.groups()
                publish_date = f'{day}/{month_to_number(month)}/{year}'
                print('publish date >>> ',publish_date)
            elif re.match(r'\w{3,} \d{1}, \d{4}', pub_date): # format: Jan 12, 2023
                date_obj = re.search(r'(\w{3,}) (\d{1}), (\d{4})', pub_date)
                month, day, year = date_obj.groups()
                publish_date = f"{day}/{month_to_number(month)}/{year}"
                print('publish date >>> ',publish_date)
            else:
                date_object = ''
                print(f"Invalid date format: {pub_date}")
                if 'ago' in pub_date:
                    elemdate0 = driver.find_elements(By.TAG_NAME,'meta')
                    if len(elemdate0)>0:
                        print("elem1")
                        for elem in elemdate0:
                            if elem.get_attribute('property') is not None:
                                if 'article:modified_time' in elem.get_attribute('property'):
                                    date_object = parser.parse(elem.get_attribute('content'))
                                elif 'dcterms:reviewed' in elem.get_attribute('property'):
                                    date_object = parser.parse(elem.get_attribute('content'))
                            elif elem.get_attribute('name') is not None:
                                if 'dcterms.date' in elem.get_attribute('name'):
                                    date_object = parser.parse(elem.get_attribute('content'))
                                elif 'modified-date' in elem.get_attribute('name'):
                                    date_object = parser.parse(elem.get_attribute('content'))
                                elif 'DC.date.modified' in elem.get_attribute('name'):
                                    date_object = parser.parse(elem.get_attribute('content'))
                            elif elem.get_attribute('og:updated_time') is not None:
                                if 'og:updated_time' in elem.get_attribute('og:updated_time'):
                                    date_object = parser.parse(elem.get_attribute('content'))
                            else:
                                break
                    elemdate2 = driver.find_elements(By.CLASS_NAME,'chakra-text')
                    if len(elemdate2)>0:
                        for elem in elemdate2: 
                            match = re.match(r'(\w{3,4})\s+(\d{1,2}),\s+(\d{4})', elem.text)
                            if match:
                                month = match.group(1)
                                day = match.group(2)
                                year = match.group(3)
                                month_dict = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
                                month_str = month_dict[month]
                                date_object = parser.parse(f"{day}/{month_str}/{year}")
                            
                    elemdate3 = driver.find_elements(By.TAG_NAME,'time')
                    if len(elemdate3)>0:
                        for elem in elemdate3:
                            pattern = '(\d{1,2}\s+)(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(\d{4})'
                            match = re.search(pattern,elem.text)
                            match1 = re.match(r'(\w{3,4})\s+(\d{1,2}),\s+(\d{4})', elem.text)

                            if elem.get_attribute('property') is not None:
                                if 'dateModified' in elem.get_attribute('property'):
                                    date_object = parser.parse(elem.text)
                            elif elem.get_attribute('class') is not None:
                                if 'jsdtTime' in elem.get_attribute('class'):
                                    date_object4 = datetime.strptime(elem.text, "Last Updated: %b %d, %Y, %I:%M %p IST")
                                    date4 = date_object4.strftime("%d/%m/%Y")
                                    publish_date = date4
                                elif 'datetime' in elem.get_attribute('class'):
                                    date_object = parser.parse(elem.text)
                            elif elem.get_attribute('datetime'):
                                if 'T' in elem.get_attribute('datetime'):
                                    date_object = parser.parse(elem.text)
                            elif match:
                                day,month,year = match.groups()
                                p_date = day + month + year
                                date_object = parser.parse(p_date)
                            elif match1:
                                month = match.group(1)
                                day = match.group(2)
                                year = match.group(3)
                                month_dict = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07", "Aug": "08", "Sept": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
                                month_str = month_dict[month]
                                publish_date = f"{day}/{month_str}/{year}"
                            else:
                                break
                    
                    elemdate4 = driver.find_elements(By.ID,'pageModified')
                    if len(elemdate4)>0:
                        for elem in elemdate4:
                            date_object = parser.parse(elem.text)
                    else:
                        elemdate5 = driver.find_elements(By.ID,'publicModified')
                        if len(elemdate5)>0:
                            for elem in elemdate5:
                                date_object = parser.parse(elem.text)
                        else:
                            elemdate6 = driver.find_elements(By.ID,'cmd_publishDate_1')
                            if len(elemdate6)>0:
                                for elem in elemdate6:
                                    date_object = parser.parse(elem.text)
                            else:
                                elemdate7 = driver.find_elements(By.CLASS_NAME,'news-item-date')
                                if len(elemdate7)>0:
                                    for elem in elemdate7:
                                        date_object = parser.parse(elem.text)
                                else:
                                    elemdate8 = driver.find_elements(By.CLASS_NAME,'dateInfo')
                                    if len(elemdate8)>0:
                                        for elem in elemdate8:
                                            date_object = parser.parse(elem.text)
                                    else:
                                        elemdate9 = driver.find_elements(By.CLASS_NAME,'ecl-col-12 ecl-col-m-4')
                                        if len(elemdate9)>0:
                                            for elem in elemdate9:
                                                date_object = parser.parse(elem.text)
                                        else:
                                            elemdate10 = driver.find_elements(By.TAG_NAME,'span')
                                            if len(elemdate10)>0:
                                                for elem in elemdate10:
                                                    if elem.get_attribute('itemprop') is not None:
                                                        if 'datePublished' in elem.get_attribute('itemprop'):
                                                            date_object = parser.parse(elem.text)
                                            else:
                                                elemdate11 = driver.find_elements(By.CLASS_NAME,'article-header-blog__date')
                                                if len(elemdate11)>0:
                                                    for elem in elemdate11:
                                                        date_object = parser.parse(elem.text)
                                                else:
                                                    elemdate12 = driver.find_elements(By.CLASS_NAME,'gem-c-metadata__definition')
                                                    if len(elemdate12)>0:
                                                        for elem in elemdate12:
                                                            date_object = parser.parse(elem.text)
                                                    else:
                                                        elemdate13 = driver.find_elements(By.CLASS_NAME,'mb-no')
                                                        if len(elemdate13)>0:
                                                            for elem in elemdate13:
                                                                date_object = parser.parse(elem.text)

                publish_date = date_object.strftime("%d/%m/%Y")

            df.loc[u] = [url[u],title,publish_date,str(res)]

    except Exception as e:
        print("Exception >>> ",e)
        # driver.execute_script("window.stop();")
    df.drop(df.loc[df['title']==''].index, inplace=True)
    df.drop(df.loc[df['data']==''].index, inplace=True)
    df = df.reset_index()
    df.drop('index',axis=1,inplace=True)

    news_path = 'F:/python-webscrap-policy-main'
    if not os.path.exists(news_path):
        os.mkdir(news_path)
    country_path = news_path+"/"+country_name
    if not os.path.exists(country_path):
        os.mkdir(country_path)
    path = country_path+"/CyberSecurity"
    if not os.path.exists(path):
        os.mkdir(path)
    df.to_csv(f'{path}/{country_name}_cyber_security_news.csv')

    urls = []
    for u in df["url_link"]:
        urls.append(u)
    
    meta_data = [country_name,len(df),urls]
    
    with open("metadata.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerow(meta_data)
    
    log_data = [country_name,urls,indian_time1.strftime("%d/%m/%Y %H:%M:%S"),'-']
    with open('logdetails.csv','a') as f:
        writer = csv.writer(f)
        writer.writerow(log_data)

    print('------------>>>>>>>> details extracted >>>>>>>>>---------------')

def month_to_number(month):
    month_dict = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                  'Jul': '07', 'Aug': '08', 'Sept': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
    return month_dict[month]

def advisory_detail_extraction(url,date,country_name):
    df = pd.DataFrame(columns=['url_link','title','published_date','data'])
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(chrome_options=options,service=ChromeService(ChromeDriverManager().install()))
    indian_tz1 = pytz.timezone('Asia/Kolkata')
    indian_time1 = datetime.now(indian_tz1)
    try:
        for u in range(len(url)):
            indian_tz = pytz.timezone('Asia/Kolkata')
            indian_time = datetime.now(indian_tz)
            
            pub_date = date[u]
            data = []
            title = ''
            res = ''
            publish_date = ''

            print('url : ',url[u])
            print('scrape time >>> ',indian_time.strftime("%d/%m/%Y %H:%M:%S"))
            driver.get(url[u])
            time.sleep(5)
            elem1 = driver.find_elements(By.TAG_NAME,"h1")
            if len(elem1)>0:
                for elem in elem1:
                    title=elem.text
            else:
                elem3 = driver.find_element(By.TAG_NAME,"h2")
                title=elem.text

            elem2 = driver.find_elements(By.CLASS_NAME,"container")
            if len(elem2)>0:
                for elem in elem2:
                    data.append(translator.translate(elem.text).text)
            else:
                elem4 = driver.find_elements(By.TAG_NAME,'p')
                if len(elem4)>0:
                    for elem in elem4:
                        data.append(translator.translate(elem.text).text)
                else:
                    elem5 = driver.find_elements(By.TAG_NAME,'span')
                    if len(elem5)>0:
                        for elem in elem5:
                            data.append(translator.translate(elem.text).text)
                    else:
                        elem6 = driver.find_elements(By.CLASS_NAME,'main-container')
                        if len(elem6)>0:
                            for elem in elem6:
                                data.append(translator.translate(elem.text).text)
                        else:
                            elem7 = driver.find_elements(By.TAG_NAME,'main')
                            if len(elem7)>0:
                                for elem in elem7:
                                    data.append(translator.translate(elem.text).text)
                            else:
                                elem8 = driver.find_elements(By.CLASS_NAME,'content')
                                if len(elem8)>0:
                                    for elem in elem8:
                                        data.append(translator.translate(elem.text).text)
                                else:
                                    elem9 = driver.find_elements(By.CLASS_NAME,'main')
                                    if len(elem9)>0:
                                        for elem in elem9:
                                            data.append(translator.translate(elem.text).text)
                                    else:
                                        elemdate11 = driver.find_elements(By.CLASS_NAME,'article-header-blog__date')
                                        if len(elemdate11)>0:
                                            for elem in elemdate11:
                                                date_object = parser.parse(elem.text)
                                        else:
                                            elemdate12 = driver.find_elements(By.CLASS_NAME,'gem-c-metadata__definition')
                                            if len(elemdate12)>0:
                                                for elem in elemdate12:
                                                    date_object = parser.parse(elem.text)
                                            else:
                                                elemdate13 = driver.find_elements(By.CLASS_NAME,'article-header-blog__date')
                                                if len(elemdate13)>0:
                                                    for elem in elemdate13:
                                                        date_object = parser.parse(elem.text)
            
            #print('title : ',head[0])
            listToStr = ' '.join([str(elem) for elem in data])
            res = re.sub(' +', ' ', listToStr)
            #print('data : ',str(res))

            if re.match(r'\d{2} \w{3} \d{4}', pub_date): # format: 25 Oct 2022
                date_obj = re.search(r'(\d{2}) (\w{3}) (\d{4})', pub_date)
                day, month, year = date_obj.groups()
                publish_date = f'{day}/{month_to_number(month)}/{year}'
                print('publish date >>> ',publish_date)
            elif re.match(r'\w{3,} \d{2}, \d{4}', pub_date): # format: Jan 12, 2023
                date_obj = re.search(r'(\w{3,}) (\d{2}), (\d{4})', pub_date)
                month, day, year = date_obj.groups()
                publish_date = f"{day}/{month_to_number(month)}/{year}"
                print('publish date >>> ',publish_date)
            elif re.match(r'\d{1} \w{3} \d{4}', pub_date): # format: 25 Oct 2022
                date_obj = re.search(r'(\d{1}) (\w{3}) (\d{4})', pub_date)
                day, month, year = date_obj.groups()
                publish_date = f'{day}/{month_to_number(month)}/{year}'
                print('publish date >>> ',publish_date)
            elif re.match(r'\d{2} \w{4} \d{4}', pub_date): # format: 25 Oct 2022
                date_obj = re.search(r'(\d{2}) (\w{4}) (\d{4})', pub_date)
                day, month, year = date_obj.groups()
                publish_date = f'{day}/{month_to_number(month)}/{year}'
                print('publish date >>> ',publish_date)
            elif re.match(r'\w{3,} \d{1}, \d{4}', pub_date): # format: Jan 12, 2023
                date_obj = re.search(r'(\w{3,}) (\d{1}), (\d{4})', pub_date)
                month, day, year = date_obj.groups()
                publish_date = f"{day}/{month_to_number(month)}/{year}"
                print('publish date >>> ',publish_date)
            else:
                date_object = ''
                print(f"Invalid date format: {pub_date}")
                if 'ago' in pub_date:
                    elemdate0 = driver.find_elements(By.TAG_NAME,'meta')
                    if len(elemdate0)>0:
                        print("elem1")
                        for elem in elemdate0:
                            if elem.get_attribute('property') is not None:
                                if 'article:modified_time' in elem.get_attribute('property'):
                                    date_object = parser.parse(elem.get_attribute('content'))
                                elif 'dcterms:reviewed' in elem.get_attribute('property'):
                                    date_object = parser.parse(elem.get_attribute('content'))
                            elif elem.get_attribute('name') is not None:
                                if 'dcterms.date' in elem.get_attribute('name'):
                                    date_object = parser.parse(elem.get_attribute('content'))
                                elif 'modified-date' in elem.get_attribute('name'):
                                    date_object = parser.parse(elem.get_attribute('content'))
                                elif 'DC.date.modified' in elem.get_attribute('name'):
                                    date_object = parser.parse(elem.get_attribute('content'))
                            elif elem.get_attribute('og:updated_time') is not None:
                                if 'og:updated_time' in elem.get_attribute('og:updated_time'):
                                    date_object = parser.parse(elem.get_attribute('content'))
                            else:
                                break
                    elemdate2 = driver.find_elements(By.CLASS_NAME,'chakra-text')
                    if len(elemdate2)>0:
                        for elem in elemdate2: 
                            match = re.match(r'(\w{3,4})\s+(\d{1,2}),\s+(\d{4})', elem.text)
                            if match:
                                month = match.group(1)
                                day = match.group(2)
                                year = match.group(3)
                                month_dict = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
                                month_str = month_dict[month]
                                date_object = parser.parse(f"{day}/{month_str}/{year}")
                            
                    elemdate3 = driver.find_elements(By.TAG_NAME,'time')
                    if len(elemdate3)>0:
                        for elem in elemdate3:
                            pattern = '(\d{1,2}\s+)(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(\d{4})'
                            match = re.search(pattern,elem.text)
                            match1 = re.match(r'(\w{3,4})\s+(\d{1,2}),\s+(\d{4})', elem.text)

                            if elem.get_attribute('property') is not None:
                                if 'dateModified' in elem.get_attribute('property'):
                                    date_object = parser.parse(elem.text)
                            elif elem.get_attribute('class') is not None:
                                if 'jsdtTime' in elem.get_attribute('class'):
                                    date_object4 = datetime.strptime(elem.text, "Last Updated: %b %d, %Y, %I:%M %p IST")
                                    date4 = date_object4.strftime("%d/%m/%Y")
                                    publish_date = date4
                                elif 'datetime' in elem.get_attribute('class'):
                                    date_object = parser.parse(elem.text)
                            elif elem.get_attribute('datetime'):
                                if 'T' in elem.get_attribute('datetime'):
                                    date_object = parser.parse(elem.text)
                            elif match:
                                day,month,year = match.groups()
                                p_date = day + month + year
                                date_object = parser.parse(p_date)
                            elif match1:
                                month = match.group(1)
                                day = match.group(2)
                                year = match.group(3)
                                month_dict = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07", "Aug": "08", "Sept": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
                                month_str = month_dict[month]
                                publish_date = f"{day}/{month_str}/{year}"
                            else:
                                break
                    
                    elemdate4 = driver.find_elements(By.ID,'pageModified')
                    if len(elemdate4)>0:
                        for elem in elemdate4:
                            date_object = parser.parse(elem.text)
                    else:
                        elemdate5 = driver.find_elements(By.ID,'publicModified')
                        if len(elemdate5)>0:
                            for elem in elemdate5:
                                date_object = parser.parse(elem.text)
                        else:
                            elemdate6 = driver.find_elements(By.ID,'cmd_publishDate_1')
                            if len(elemdate6)>0:
                                for elem in elemdate6:
                                    date_object = parser.parse(elem.text)
                            else:
                                elemdate7 = driver.find_elements(By.CLASS_NAME,'news-item-date')
                                if len(elemdate7)>0:
                                    for elem in elemdate7:
                                        date_object = parser.parse(elem.text)
                                else:
                                    elemdate8 = driver.find_elements(By.CLASS_NAME,'dateInfo')
                                    if len(elemdate8)>0:
                                        for elem in elemdate8:
                                            date_object = parser.parse(elem.text)
                                    else:
                                        elemdate9 = driver.find_elements(By.CLASS_NAME,'ecl-col-12 ecl-col-m-4')
                                        if len(elemdate9)>0:
                                            for elem in elemdate9:
                                                date_object = parser.parse(elem.text)
                                        else:
                                            elemdate10 = driver.find_elements(By.TAG_NAME,'span')
                                            if len(elemdate10)>0:
                                                for elem in elemdate10:
                                                    if elem.get_attribute('itemprop') is not None:
                                                        if 'datePublished' in elem.get_attribute('itemprop'):
                                                            date_object = parser.parse(elem.text)
                                            else:
                                                elemdate11 = driver.find_elements(By.CLASS_NAME,'article-header-blog__date')
                                                if len(elemdate11)>0:
                                                    for elem in elemdate11:
                                                        date_object = parser.parse(elem.text)
                                                else:
                                                    elemdate12 = driver.find_elements(By.CLASS_NAME,'gem-c-metadata__definition')
                                                    if len(elemdate12)>0:
                                                        for elem in elemdate12:
                                                            date_object = parser.parse(elem.text)
                                                    else:
                                                        elemdate13 = driver.find_elements(By.CLASS_NAME,'mb-no')
                                                        if len(elemdate13)>0:
                                                            for elem in elemdate13:
                                                                date_object = parser.parse(elem.text)

                publish_date = date_object.strftime("%d/%m/%Y")

            df.loc[u] = [url[u],title,publish_date,str(res)]

    except Exception as e:
        print("Exception >>> ",e)
        # driver.execute_script("window.stop();")
    df.drop(df.loc[df['title']==''].index, inplace=True)
    df.drop(df.loc[df['data']==''].index, inplace=True)
    df = df.reset_index()
    df.drop('index',axis=1,inplace=True)

    news_path = 'F:/python-webscrap-policy-main'
    if not os.path.exists(news_path):
        os.mkdir(news_path)
    country_path = news_path+"/"+country_name
    if not os.path.exists(country_path):
        os.mkdir(country_path)
    path = country_path+"/CyberSecurity"
    if not os.path.exists(path):
        os.mkdir(path)
    df.to_csv(f'{path}/{country_name}_cyber_security_advisory_notes.csv')

    urls = []
    for u in df["url_link"]:
        urls.append(u)
    
    meta_data = [country_name,len(df),urls]
    
    with open("advisory_metadata.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerow(meta_data)
    
    log_data = [country_name,urls,indian_time1.strftime("%d/%m/%Y %H:%M:%S"),'-']
    with open('advisory_logdetails.csv','a') as f:
        writer = csv.writer(f)
        writer.writerow(log_data)

    print('------------>>>>>>>> details extracted >>>>>>>>>---------------')
       
#detail_extraction(dic,'Argentina')