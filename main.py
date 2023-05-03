#importing necessary libraries
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
import os

translator = Translator()
headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36' } 

#finding authorized extension of country
def extension_for_url(country):
    df = pd.read_csv("WebScrap.csv")
    key =[]
    for i in df['Country']:
        if country.replace(" ",'').lower() in i.lower().replace(" ",''):
            x = (df.loc[(df['Country'] == i )]).values.tolist()
            url_kwy = [i for i in x[0][1:] if str(i) != 'nan']
            key += url_kwy
    ke = list(set(key))
    return ke

#get the list of authorized urls
def filter1(links,country_name):
    filter1_links = list() 
    https_links = [link for link in links if 'https://' in link.lower()] 
    authentic_site_extension = extension_for_url(country_name)
    print("extension name : ",authentic_site_extension)
    com_ex = ['.gov','.org','.eu','itu']
    c_ex = [i for i in authentic_site_extension if i not in com_ex]
    print('length >>>' ,len(c_ex))
    if len(c_ex)<=0:
        c_ex = authentic_site_extension
        first_stage_filter = [link for i in authentic_site_extension for link in https_links if i.lower() in link.lower()]
        first_stage_filter = https_links if len(first_stage_filter) == 0 else first_stage_filter
        filter1_links = list(set(first_stage_filter))
    else:
        first_stage_filter = [link for i in authentic_site_extension for link in https_links if i.lower() in link.lower()]
        first_stage_filter = https_links if len(first_stage_filter) == 0 else first_stage_filter
        filter1_links = list(set(first_stage_filter))
    return filter1_links,c_ex

#match the url keywords and get the list of authenticated urls
def filter_sublinks(sublink_list,main_extension):
    df = pd.read_excel("Regulator.xlsx", sheet_name='keywords')
    keyword_list = [i for i in df['Url_keywords'].tolist() if str(i) != 'nan']
    filter2_sublinks = []
    for keyword in keyword_list:
        y = keyword.translate(str.maketrans('', '', string.punctuation))
        for each_sublink in sublink_list:
            if main_extension in each_sublink:
                 filter2_sublinks.append(each_sublink)            
            x = each_sublink.translate(str.maketrans('', '', string.punctuation))
            if y.lower() in x.lower():
                filter2_sublinks.append(each_sublink)
    filter2_sublinks = list(set(filter2_sublinks))
    return filter2_sublinks

#remove the social media urls
def filter3(link_list): 
    l = ['linkedin','facebook','twitter','youtube','instagram','wiki','contact','yahoo','whatsapp','login','signin','unodc','cyberwiser.eu']
    q = [link for link in link_list if any(ext in link for ext in l)]
    links = [i for i in link_list if i not in q]
    return links

#site must be start with www
def find_site_name(x):
    site_name = [j for j in x.split("/") if 'www' in j]
    return site_name

#get the list of unique urls
def unique_filter_links(list_of_links):
    un_web_site = []
    for i in list_of_links:
        site_name = find_site_name(i)
        res = any(site_name[0] in sub for sub in un_web_site)
        if res == False:
            un_web_site.append(i)
    return un_web_site

#get the list of filtered news links from another source(i.e, Google Newstab)
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

#get the final list of news links
def filter_final_news_links(links):
    lst = ['cybersecurity','cybersecurity-act','act','cyber','policy','information','strategies','attacks','threats','security']
    keyword_list = [i for i in lst if str(i) != 'nan']
    url = []
    list = []
    lnk = []
    for link in links:
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
#get the list of filtered advisory links from another source(i.e, Google Newstab)
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

data_content = pd.read_excel("Regulator.xlsx",sheet_name="keywords")
keyword_list = [i for i in data_content['news_title_keyword'].tolist() if str(i) != 'nan']
content_list = [i for i in data_content['content_keywords'].tolist() if str(i) != 'nan']
advisory_list = [i for i in data_content['advisory_keyword'].tolist() if str(i) != 'nan']
data_key = pd.read_excel('Regulator.xlsx',sheet_name='keywords')
url_keyword = []
for i in data_key['news_url_keywords']:
    if str(i) == 'nan':
        pass
    else:
        url_keyword.append(i)

#extract the news and advisories sublinks
def extract_news_advisory_sublinks(links,c_ex):
    news_links = []
    advisory_links = []
    #------------------extract sublinks---------------------------------
    for link in links:
        print("URL for news ------------------>>>>>>> ",link)

        options = webdriver.ChromeOptions()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
        driver = webdriver.Chrome(chrome_options=options,service=ChromeService(ChromeDriverManager().install()))
        driver.maximize_window()
        driver.get(link)
        driver.set_page_load_timeout(60)
        time.sleep(2)
        current_link = driver.current_url

        list_=[] 
        lnk=driver.find_elements(By.XPATH, "//a[@href]")
        try:
            for i in lnk:
                list_.append(str(i.get_attribute('href'))) 
        except:
            pass
        final_list = [link]+list_
        sublink_list = list(set(final_list))
        driver.quit()

        # print("raw_sublink >>> ",sublink_list)
        print("sublink list :",len(sublink_list))
        Filter_Sublinks = filter_sublinks(sublink_list,c_ex[0])
        u_filter_sublinks = filter3(Filter_Sublinks)
        https_filtersublinks = [sublink for sublink in u_filter_sublinks if 'https://' in sublink.lower()]

        print("sublinks after filter >>>>>>>>>>>>>>> ",https_filtersublinks)
        print("len of filter sublink :",len(https_filtersublinks))

        for lnk in https_filtersublinks:
            check_data = any(item in lnk for item in url_keyword)
            if check_data == True:
                news_links.append(lnk)
        
        for lnk in https_filtersublinks:
            check = any(item in lnk for item in advisory_list)
            if check==True:
                advisory_links.append(lnk)
    
    nws_lnk = []
    for i in news_links:
        if i not in nws_lnk:
            if '#' in i:
                pass
            else:
                nws_lnk.append(i) 
    nws_lnk_1 = filter_final_news_links(nws_lnk)
    
    advisory_link = []
    for i in advisory_links:
        if i not in advisory_link:
            if '#' in i:
                pass
            else:
                advisory_link.append(i) 
    advisory_link_1 = filter_advisory_sublinks(advisory_link)

    
    #-------------------for news inner sub links------------------------------
    for l in nws_lnk_1:
        print("URL for news ------------------>>>>>>> ",l)

        options = webdriver.ChromeOptions()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
        driver = webdriver.Chrome(chrome_options=options,service=ChromeService(ChromeDriverManager().install()))
        driver.maximize_window()
        driver.get(l)
        driver.set_page_load_timeout(60)
        time.sleep(2)
        current_link = driver.current_url

        list_=[] 
        lnk=driver.find_elements(By.XPATH, "//a[@href]")
        try:
            for i in lnk:
                list_.append(str(i.get_attribute('href'))) 
        except:
            pass
        final_list = [l]+list_
        sublink_list = list(set(final_list))
        driver.quit()

        # print("raw_sublink >>> ",sublink_list)
        print("sublink list :",len(sublink_list))
        Filter_Sublinks = filter_sublinks(sublink_list,c_ex[0])
        u_filter_sublinks = filter3(Filter_Sublinks)
        https_filtersublinks = [sublink for sublink in u_filter_sublinks if 'https://' in sublink.lower()]

        print("sublinks after filter >>>>>>>>>>>>>>> ",https_filtersublinks)
        print("len of filter sublink :",len(https_filtersublinks))
        
        for http_lnk in https_filtersublinks:
            check_data = any(item in http_lnk for item in url_keyword)
            if check_data == True:
                news_links.append(http_lnk)
        
        for http_sublnk in https_filtersublinks:
            check = any(item in http_sublnk for item in advisory_list)
            if check==True:
                advisory_links.append(http_sublnk)
    
    #-------------------for adviosry inner sub links------------------------------
    for l in advisory_link_1:
        print("URL for avisory ------------------>>>>>>> ",l)

        options = webdriver.ChromeOptions()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
        driver = webdriver.Chrome(chrome_options=options,service=ChromeService(ChromeDriverManager().install()))
        driver.maximize_window()
        driver.get(l)
        driver.set_page_load_timeout(60)
        time.sleep(2)
        current_link = driver.current_url

        list_=[] 
        lnk=driver.find_elements(By.XPATH, "//a[@href]")
        try:
            for i in lnk:
                list_.append(str(i.get_attribute('href'))) 
        except:
            pass
        final_list = [l]+list_
        sublink_list = list(set(final_list))
        driver.quit()

        # print("raw_sublink >>> ",sublink_list)
        print("sublink list :",len(sublink_list))
        Filter_Sublinks = filter_sublinks(sublink_list,c_ex[0])
        u_filter_sublinks = filter3(Filter_Sublinks)
        https_filtersublinks = [sublink for sublink in u_filter_sublinks if 'https://' in sublink.lower()]

        print("sublinks after filter >>>>>>>>>>>>>>> ",https_filtersublinks)
        print("len of filter sublink :",len(https_filtersublinks))
        
        for lnk in https_filtersublinks:
            check_data = any(item in lnk for item in url_keyword)
            if check_data == True:
                news_links.append(lnk)
        
        for lnk in https_filtersublinks:
            check = any(item in lnk for item in advisory_list)
            if check==True:
                advisory_links.append(lnk)
    
    nws_l = []
    for i in news_links:
        if i not in nws_l:
            if '#' in i:
                pass
            else:
                nws_l.append(i)
    
    advisory_lnk = []
    for i in advisory_links:
        if i not in advisory_lnk:
            if '#' in i:
                pass
            else:
                advisory_lnk.append(i) 
    
    filter_news_sub_link = filter_final_news_links(nws_l)
    filter_advisory_sub_link = filter_advisory_sublinks(advisory_lnk)

    return list(set(filter_news_sub_link)),list(set(filter_advisory_sub_link))

#news and advisory detail extract
#common code to extract the detail of news and advisory
def news_advisory_extract(links):
    lst = []
    for nws in links:
        indian_tz = pytz.timezone('Asia/Kolkata')
        indian_time = datetime.datetime.now(indian_tz)
        dic={}
        data = []
        title = ''
        publish_date = ''
        date_object=''
        options = webdriver.ChromeOptions()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
        driver = webdriver.Chrome(chrome_options=options,service=ChromeService(ChromeDriverManager().install()))
        print("news link >>>>>",nws)
        print("scrape time >>> ",indian_time.strftime("%d/%m/%Y %H:%M:%S"))

        try:
            driver.get(nws)
            driver.set_page_load_timeout(60)
            time.sleep(2)
            elem1 = driver.find_elements(By.TAG_NAME,"h1")
            if len(elem1)>0:
                for elem in elem1:
                    check = any(item in translator.translate(elem.text.lower()).text for item in keyword_list)
                    print('title checking>>>',check)
                    if check==True:
                        title=elem.text
                        print("-------filter1 pass ---------")
            else:
                elem3 = driver.find_elements(By.TAG_NAME,"h2")
                for elem in elem3:
                    check = any(item in translator.translate(elem.text.lower()).text for item in keyword_list)
                    print('title checking>>>',check)
                    if check==True:
                        title=elem.text
                        print("-------filter1 pass ---------")

            elem2 = driver.find_elements(By.TAG_NAME,"main")
            if len(elem2)>0:
                for elem in elem2:
                    data.append(translator.translate(elem.text).text)
            else:
                elem4 = driver.find_elements(By.CLASS_NAME,'main')
                if len(elem4)>0:
                    for elem in elem4:
                        data.append(translator.translate(elem.text).text)
                else:
                    elem5 = driver.find_elements(By.CLASS_NAME,'main-container')
                    if len(elem5)>0:
                        for elem in elem5:
                            data.append(translator.translate(elem.text).text)
                    else:
                        elem6 = driver.find_elements(By.CLASS_NAME,'container')
                        if len(elem6)>0:
                            for elem in elem6:
                                data.append(translator.translate(elem.text).text)
                        else:
                            elem7 = driver.find_elements(By.TAG_NAME,'p')
                            if len(elem7)>0:
                                for elem in elem7:
                                    data.append(translator.translate(elem.text).text)
                            else:
                                elem8 = driver.find_elements(By.CLASS_NAME,'content')
                                if len(elem8)>0:
                                    for elem in elem8:
                                        data.append(translator.translate(elem.text).text)
                                else:
                                    elem9 = driver.find_elements(By.TAG_NAME,'span')
                                    if len(elem9)>0:
                                        for elem in elem9:
                                            data.append(translator.translate(elem.text).text)

            
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
                                                else:
                                                    elemdate13 = driver.find_elements(By.CLASS_NAME,'article-header-blog__date')
                                                    if len(elemdate13)>0:
                                                        for elem in elemdate13:
                                                            date_object = parser.parse(elem.text)

            publish_date = date_object.strftime("%d/%m/%Y")
            print('data >>> ',data)
            #data1 = ['cyber','security','information',country_name.lower()]
            details = ''
            for i in data:
                #check_d = all(item in i.lower() for item in data1)
                #if check_d==True:
                check_data = any(item in i.lower() for item in content_list)
                print('details >>> ',check_data)
                if check_data==True:
                    details+=''.join(filter(lambda x:x in string.printable,i))
                    dic["url_link"] = nws
                    dic["title"] = translator.translate(title).text
                    dic["published_date"] = publish_date
                    dic["data"] = translator.translate(details.replace("\n"," ")).text
                    #print("details",details)
                    print('------filter2 pass------')  
                lst.append(dic)
        except:
            driver.quit()   
    
    return lst

#storing of news data into csv, maintaining logfile and meta data details
def store_news_details(nws_lst,country_name):
    indian_tz = pytz.timezone('Asia/Kolkata')
    indian_time = datetime.datetime.now(indian_tz)
    if len(nws_lst)>0:
        res_data = [d for d in nws_lst if d]
        dt = pd.DataFrame(res_data)
        dt = dt.drop_duplicates(keep="first")
        dt.drop(dt.loc[dt['title']==''].index, inplace=True)
        dt.drop(dt.loc[dt['data']==''].index, inplace=True)
        dt.drop(dt.loc[dt['published_date']==''].index,inplace=True)
        dt = dt.reset_index()
        dt.drop('index',axis=1,inplace=True)
        print(dt)
        
        if dt.empty:
            print('--------------#-----------------#-------------------#-----------------#-------------------#-------------------')
            print('searching for >>>>> news related to ',country_name)
            news_URL = res.news_URL(country_name)
            all_news_links = news_link.link_extract(news_URL,country_name)
            print('all news links >>>>',all_news_links)
            
            filter1_news_link,c_nws_ex = filter1(all_news_links.keys(),country_name)
            filter2_news_link = filter_news_sublinks(filter1_news_link)
            
            #------link filteration------
            filtered_link = []
            for l in filter2_news_link:
                if l not in filtered_link:
                    filtered_link.append(l)
            print('filtered news link : ',filtered_link)

            news_lnk = {}
            for l in filtered_link:
                news_lnk[l] = all_news_links.get(l)
            print('news links with dictionary : ',news_lnk)
            
            nws_url = list(news_lnk.keys())
            nws_date = list(news_lnk.values())
            detail_extract.detail_extraction(nws_url,nws_date,country_name)

        else:            
            news_path = 'F:/python-webscrap-policy-main'
            if not os.path.exists(news_path):
                os.mkdir(news_path)
            country_path = news_path+"/"+country_name
            if not os.path.exists(country_path):
                os.mkdir(country_path)
            path = country_path+"/CyberSecurity"
            if not os.path.exists(path):
                os.mkdir(path)
            dt.to_csv(f'{path}/{country_name}_cyber_security_news.csv')

            urls = []
            for u in dt["url_link"]:
                urls.append(u)
            meta_data = [country_name,len(dt),urls]

            with open("metadata.csv", "a") as f:
                writer = csv.writer(f)
                writer.writerow(meta_data)
            
            log_data = [country_name,urls,indian_time.strftime("%d/%m/%Y %H:%M:%S"),'-']
            with open('logdetails.csv','a') as f:
                writer = csv.writer(f)
                writer.writerow(log_data)

            print('------------>>>>>>>> details extracted >>>>>>>>>---------------')
    else:
        print('--------------#-----------------#-------------------#-----------------#-------------------#-------------------')
        print('searching for >>>>> news related to ',country_name)
        news_URL = res.news_URL(country_name)
        all_news_links = news_link.link_extract(news_URL,country_name)
        
        filter1_news_link,c_nws_ex = filter1(all_news_links.keys(),country_name)
        filter2_news_link = filter_news_sublinks(filter1_news_link)
        
        #------link filteration------
        filtered_link = []
        for l in filter2_news_link:
            if l not in filtered_link:
                filtered_link.append(l)
        print('filtered news link : ',filtered_link)

        news_lnk = {}
        for l in filtered_link:
            news_lnk[l] = all_news_links.get(l)
        print('news links with dictionary : ',news_lnk)
        
        nws_url = list(news_lnk.keys())
        nws_date = list(news_lnk.values())
        detail_extract.detail_extraction(nws_url,nws_date,country_name)

#storing of advisory data into csv, maintaining logfile and meta data detailsv
def store_advisory_details(ad_lst,country_name):
    indian_tz = pytz.timezone('Asia/Kolkata')
    indian_time = datetime.datetime.now(indian_tz)
    if len(ad_lst)>0:
        res_data1 = [d for d in ad_lst if d]
        ad_dt = pd.DataFrame(res_data1)
        ad_dt = ad_dt.drop_duplicates(keep="first")
        ad_dt.drop(ad_dt.loc[ad_dt['title']==''].index, inplace=True)
        ad_dt.drop(ad_dt.loc[ad_dt['data']==''].index, inplace=True)
        ad_dt.drop(ad_dt.loc[ad_dt['published_date']==''].index,inplace=True)
        ad_dt = ad_dt.reset_index()
        ad_dt.drop('index',axis=1,inplace=True)
        print(ad_dt)
        
        if ad_dt.empty:
            print('--------------#-----------------#-------------------#-----------------#-------------------#-------------------')
            print('searching for >>>>> Cyber Security Advosry Notes')
            ads_URL = res.news_URL(country_name)
            all_ads_links = news_link.link_extract(ads_URL,country_name)
            print('all news links >>>>',all_ads_links)
            
            filter1_ads_link,c_nws_ex = filter1(all_ads_links.keys(),country_name)
            filter2_ads_link = filter_advisory_sublinks(filter1_ads_link)
            
            #------link filteration------
            filtered_ads_link = []
            for l in filter2_ads_link:
                if l not in filtered_ads_link:
                    filtered_ads_link.append(l)
            print('filtered news link : ',filtered_ads_link)

            ads_lnk = {}
            for l in filtered_ads_link:
                ads_lnk[l] = all_ads_links.get(l)
            print('news links with dictionary : ',ads_lnk)
            
            ads_url = list(ads_lnk.keys())
            ads_date = list(ads_lnk.values())
            detail_extract.advisory_detail_extraction(ads_url,ads_date,country_name)

        else:            
            news_path = 'F:/python-webscrap-policy-main'
            if not os.path.exists(news_path):
                os.mkdir(news_path)
            country_path = news_path+"/"+country_name+"/CyberSecurity"
            if not os.path.exists(country_path):
                os.mkdir(country_path)
            ad_dt.to_csv(f'{country_path}/{country_name}_cyber_security_advisory_notes.csv')

            ads_urls = []
            for u in ad_dt["url_link"]:
                ads_urls.append(u)
            ads_meta_data = [country_name,len(ad_dt),ads_urls]

            with open("advisory_metadata.csv", "a") as f:
                writer = csv.writer(f)
                writer.writerow(ads_meta_data)
            
            ads_log_data = [country_name,ads_urls,indian_time.strftime("%d/%m/%Y %H:%M:%S"),'-']
            with open('advisory_logdetails.csv','a') as f:
                writer = csv.writer(f)
                writer.writerow(ads_log_data)

            print('------------>>>>>>>> details extracted >>>>>>>>>---------------')
    else:
        print('--------------#-----------------#-------------------#-----------------#-------------------#-------------------')
        print('searching for >>>>> Cyber Security Advosry Notes')
        ads_URL = res.news_URL(country_name)
        all_ads_links = news_link.link_extract(ads_URL,country_name)
        print('all news links >>>>',all_ads_links)
        
        filter1_ads_link,c_nws_ex = filter1(all_ads_links.keys(),country_name)
        filter2_ads_link = filter_advisory_sublinks(filter1_ads_link)
        
        #------link filteration------
        filtered_ads_link = []
        for l in filter2_ads_link:
            if l not in filtered_ads_link:
                filtered_ads_link.append(l)
        print('filtered news link : ',filtered_ads_link)

        ads_lnk = {}
        for l in filtered_ads_link:
            ads_lnk[l] = all_ads_links.get(l)
        print('news links with dictionary : ',ads_lnk)
        
        ads_url = list(ads_lnk.keys())
        ads_date = list(ads_lnk.values())
        detail_extract.advisory_detail_extraction(ads_url,ads_date,country_name)

#-------------------------------cyber security news advisory extraction-------------------------------
#--------main---------part-------------start---------
def extract_news(country_name):
    raw_links=[]
    try:
        from googlesearch import search
    except ImportError:
        print("No module named 'google' found")
    #print("Enter Country Name : ")
    #user_response = input()
    print('country : ',country_name)
    user_response = country_name
    user_response = "cyber security policy/strategy in "+user_response
    print("user_responce >>> ",user_response)
   
    for j in search(user_response, tld="co.in", num=1, stop=40, pause=2):
    #for j in search(user_response):
        raw_links.append(j)    


    print("raw links >>>>>>>>>>>>>>>>>>>>>>>>>>>>> ",raw_links)

    filter1links,c_ex = filter1(raw_links,country_name)
    filter2links = filter_sublinks(filter1links,c_ex[0])
    filter3links = filter3(filter2links)

    links = filter3links
    print("filter links >>>>>>>>>>>>>>>>>>>>>> ",links)
    news_link,advisory_link=extract_news_advisory_sublinks(links,c_ex)
    
    nws_lst = news_advisory_extract(news_link)
    ads_lst = news_advisory_extract(advisory_link)

    store_news_details(nws_lst,country_name)
    store_advisory_details(ads_lst,country_name)

cnt = pd.read_csv('country.csv')
for c in cnt["Country_Name"]:
    extract_news(c)
#-----------main part ends-----------------------------------------------