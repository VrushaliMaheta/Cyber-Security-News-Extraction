# import necessary library
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import string
import requests
import time 
from datetime import date
from selenium.webdriver.chrome.service import Service as ChromeService
from googlesearch import search
import openpyxl
import re
import numpy as np
from googletrans import Translator
import details_extraction as detail_extract
import news_link_extraction as news_link
import news_link_response as res
import csv
import datetime
import pytz
from dateutil import parser

translator = Translator()

#get the list of filtered advisory links
def filter_news_sublinks(sublink_list):
    df = pd.read_excel("Regulator.xlsx", sheet_name='keywords')
    keyword_list = [i for i in df['Url_keywords'].tolist() if str(i) != 'nan']
    url = []
    list = []
    lnk = []
    for link in sublink_list:
        str1 = link.split("/")
        if str1[-1]=='':
            s = str1[-2].split('-')
            check = any(item in s for item in keyword_list)
            if check is True:
                lnk.append(link)
        else:
            s = str1[-1].split('-')
            check = any(item in s for item in keyword_list)
            if check is True:
                lnk.append(link)

    return lnk

#get the list of filtered advisory links
def filter_advisory_sublinks(sublink_list):
    df = pd.read_excel("Regulator.xlsx", sheet_name='keywords')
    keyword_list = [i for i in df['advisory_keyword'].tolist() if str(i) != 'nan']
    url = []
    list = []
    lnk = []
    for link in sublink_list:
        str1 = link.split("/")
        if str1[-1]=='':
            s = str1[-2].split('-')
            check = any(item in s for item in keyword_list)
            if check is True:
                lnk.append(link)
        else:
            s = str1[-1].split('-')
            check = any(item in s for item in keyword_list)
            if check is True:
                lnk.append(link)

    return lnk

#finding the updation occurs in advisory or not
def news_updation(country_name,news_df):
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(chrome_options=options,service=ChromeService(ChromeDriverManager().install()))

    for i in range(len(news_df)):
        try:
            driver.get(news_df["url_link"][i])
            print('url >>> ',news_df["url_link"][i])
            time.sleep(2)

            list_=[] 
            lnk=driver.find_elements(By.XPATH, "//a[@href]")
            for l in lnk:
                list_.append(str(l.get_attribute('href'))) 
            final_list = [news_df["url_link"][i]]+list_
            sublink_list = list(set(final_list))
            ads_link = filter_news_sublinks(sublink_list)

            print(ads_link)
            link = compare_dates(ads_link,country_name)
            if len(link)>0:
                with open('logdetails.csv', 'rw+') as f:
                    reader = csv.reader(f)
                    writer = csv.writer(f)
                    next(reader)
                    for row in reader:
                        if row[0] == country_name:
                            row[3] = link
                            writer.writerow(row)
            
        except Exception as e:
        #driver.quit()
            i+=1
            print("Exception >>> ",e)

#finding the updation occurs in advisory or not
def advisory_updation(country_name,news_df):
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(chrome_options=options,service=ChromeService(ChromeDriverManager().install()))

    for i in range(len(news_df)):
        try:
            driver.get(news_df["url_link"][i])
            print('url >>> ',news_df["url_link"][i])
            time.sleep(2)

            list_=[] 
            lnk=driver.find_elements(By.XPATH, "//a[@href]")
            for l in lnk:
                list_.append(str(l.get_attribute('href'))) 
            final_list = [news_df["url_link"][i]]+list_
            sublink_list = list(set(final_list))
            ads_link = filter_advisory_sublinks(sublink_list)

            print(ads_link)
            link = compare_dates(ads_link,country_name)
            if len(link)>0:
                with open('advisory_logdetails.csv', 'rw+') as f:
                    reader = csv.reader(f)
                    writer = csv.writer(f)
                    next(reader)
                    for row in reader:
                        if row[0] == country_name:
                            row[3] = link
                            writer.writerow(row)
            
        except Exception as e:
        #driver.quit()
            i+=1
            print("Exception >>> ",e)

#open each urls and get the published date
def compare_dates(links,country_name):
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(chrome_options=options,service=ChromeService(ChromeDriverManager().install()))

    upt_link = []
    date_object = ''
    try:
        for link in links:
            print('news link >>> ',link)
            driver.get(link)
            time.sleep(3)

            elemdate0 = driver.find_elements(By.TAG_NAME,'meta')
            if len(elemdate0)>0:
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
                        elif 'dcterms.modified' in elem.get_attribute('name'):
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
                print("elem4")
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
                                            elif elem.get_attribute('class') is not None:
                                                if 'text-xxs text-cga-blue-dark mb-1 ml-2 hidden md:inline-block' in elem.get_attribute('class'):
                                                    date_object = parser.parse(elem.text)
                                                elif 'date' in elem.get_attribute('class'):
                                                    date_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s\d{1,2},\s\d{4}'

                                                    match = re.search(date_pattern, elem.text)

                                                    if match:
                                                        date_object = parser.parse(match.group(0))
                                                    else:
                                                        pass
                                                    
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
            pub_date = datetime.datetime.strptime(publish_date, "%d/%m/%Y").date()
            today = datetime.date.today()
            yesterday = today - datetime.timedelta(days=1)

            if pub_date==today:
                print('no updation')
            elif pub_date>today:
                upt_link.append(link)
                print("updation")
            elif pub_date<today:
                print('no updation')
            elif pub_date==yesterday:
                print('no updation')
            elif pub_date>yesterday:
                if pub_date==today:
                    print('no updation')
                else:
                    upt_link.append(link)
                    print("updation")
            else:
                print('no updation')

    except Exception as e:
        print('exception >>> ',e)  
        pass

    return upt_link

def main():
    cnt_data = pd.read_csv('country.csv')
    for c in cnt_data["Country_Name"]:
        print("country >>>> ",c)
        news_df = pd.read_csv(f'F:/python-webscrap-policy-main/{c}/CyberSecurity/{c}_cyber_security_news.csv')
        news_updation(c,news_df)
        ads_df = pd.read_csv(f'F:/python-webscrap-policy-main/{c}/CyberSecurity/{c}_cyber_security_advisory_notes.csv')
        advisory_updation(c,ads_df)

main()