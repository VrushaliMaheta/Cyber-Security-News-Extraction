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
import csv

def link_extract(URL,country_name):
    news_links = []
    dic = {}
    news_lnk = {}
    date = []
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(chrome_options=options,service=ChromeService(ChromeDriverManager().install()))
    try:
        driver.get(URL)
        time.sleep(5)
        while True:
            elems = driver.find_elements(By.CLASS_NAME,"WlydOe")
            for elem in elems:
                news_links.append(elem.get_attribute('href'))
            
            
            dt = driver.find_elements(By.CLASS_NAME,"YsWzw")
            for d in dt:
                date.append(d.text)
            
            for i in range(len(news_links)):
                dic[news_links[i]] = date[i] 

            next_button_class = 'pnnext' ###here insert the class of 'next button'
            driver.find_element(By.ID,next_button_class).click()
            time.sleep(30)  


    except:
        driver.execute_script("window.stop();")

    #print('All News Links : ',news_links)
    return dic

