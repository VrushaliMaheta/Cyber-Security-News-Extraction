import pandas as pd

cnt = pd.read_csv("country.csv")
countries = {}
for i in range(len(cnt["Country_Name"])):
    countries[cnt["Country_Name"][i]] = cnt["Country_code"][i]

def news_URL(user_response):
    country_name = user_response
    user_response = "news related to cyber security policy/strategy in "+user_response
    print("user_responce >>> ",user_response)

    user_response = user_response.replace(" ","+")
    user_response = user_response.replace("/","%2F")

    cnt_code = ''
    for i in countries.keys():
        if country_name in i:
            cnt_code = countries[i]

    print('country code : ',cnt_code)

    URL = "https://www.google.com/search?q="+user_response+"&gl="+cnt_code+"&tbm=nws&hl=en"

    return URL
