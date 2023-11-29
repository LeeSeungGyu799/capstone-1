from bs4 import BeautifulSoup
import requests
import re
import time
import os
import sys
import urllib.request
from urllib.parse import quote
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import pandas as pd

columns_to_check = ['article1', 'article2', 'article3']


def remove_special_characters(value):
    # NaN이나 숫자 등 문자열이 아닌 데이터는 변환하지 않음
    if pd.isnull(value) or not isinstance(value, str):
        return value
    return re.sub(r'[^\w\s]', '', value)


# 웹드라이버 설정
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# 버전에 상관 없이 os에 설치된 크롬 브라우저 사용
driver = webdriver.Chrome()
driver.implicitly_wait(3)
# 버전에 상관 없이 os에 설치된 크롬 브라우저 사용

client_id = 'jbSiw0GXFLEFoDTesC2J'
client_secret = 'U9IhEJTSLG'

naver_urls = []
postdate = []
titles = []

# 검색어 입력
keyword = input("검색할 키워드를 입력해주세요:")
encText = urllib.parse.quote(keyword)

# 검색을 끝낼 페이지 입력
end = input("\n크롤링을 끝낼 위치를 입력해주세요. (기본값:1, 최대값:100):")
if end == "":
    end = 1
else:
    end = int(end)
print("\n 1 ~ ", end, "페이지 까지 크롤링을 진행 합니다")

# 한번에 가져올 페이지 입력
display = input("\n한번에 가져올 페이지 개수를 입력해주세요.(기본값:10, 최대값: 100):")
if display == "":
    display = 10
else:
    display = int(display)
print("\n한번에 가져올 페이지 : ", display, "페이지")

for start in range(0, end * display, display):
    url = "https://openapi.naver.com/v1/search/blog?query=" + encText + "&start=" + str(start + 1) + "&display=" + str(display + 1)  # JSON 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if (rescode == 200):
        response_body = response.read()

        data = json.loads(response_body.decode('utf-8'))['items']
        for row in data:
            if ('blog.naver' in row['link']):
                naver_urls.append(row['link'])
                postdate.append(row['postdate'])
                title = row['title']
                # html태그제거
                pattern1 = '<[^>]*>'
                title = re.sub(pattern=pattern1, repl='', string=title)
                titles.append(title)
        time.sleep(2)
    else:
        print("Error Code:" + rescode)

###naver 기사 본문 및 제목 가져오기###

# ConnectionError방지
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}

contents_loc = []
contents_article_1 = []
contents_article_2 = []
contents_article_3 = []
comments_texts = []

try:
    for i in naver_urls:
        print(i)
        driver.get(i)
        time.sleep(5)  # 대기시간 변경 가능

        iframe = driver.find_element(By.ID, "mainFrame")  # id가 mainFrame이라는 요소를 찾아내고 -> iframe임
        driver.switch_to.frame(iframe)  # 이 iframe이 내가 찾고자하는 html을 포함하고 있는 내용

        source = driver.page_source
        html = BeautifulSoup(source, "html.parser")

        # 기사 텍스트만 가져오기
        content_loc = html.select("div.location_component")
        content_article_1 = html.select("div.se_component_wrap")
        content_article_2 = html.select("div.se-main-container")
        content_article_3 = html.select("div#postViewArea")
        #  list합치기
        content_loc = ''.join(str(content_loc))
        content_article_1 = ''.join(str(content_article_1))
        content_article_2 = ''.join(str(content_article_2))
        content_article_3 = ''.join(str(content_article_3))

        # html태그제거 및 텍스트 다듬기
        content_loc = re.sub(pattern=pattern1, repl='', string=content_loc)
        content_article_1 = re.sub(pattern=pattern1, repl='', string=content_article_1)
        content_article_2 = re.sub(pattern=pattern1, repl='', string=content_article_2)
        content_article_3 = re.sub(pattern=pattern1, repl='', string=content_article_3)

        pattern2 = """[\n\n\n\n\n// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}"""

        content_loc = content_loc.replace(pattern2, '')
        content_article_1 = content_article_1.replace(pattern2, '')
        content_article_2 = content_article_2.replace(pattern2, '')
        content_article_3 = content_article_3.replace(pattern2, '')

        content_loc = content_loc.replace('\n', '')
        content_article_1 = content_article_1.replace('\n', '')
        content_article_2 = content_article_2.replace('\n', '')
        content_article_3 = content_article_3.replace('\n', '')

        content_loc = content_loc.replace('\u200b', '')
        content_article_1 = content_article_1.replace('\u200b', '')
        content_article_2 = content_article_2.replace('\u200b', '')
        content_article_3 = content_article_3.replace('\u200b', '')

        contents_loc.append(content_loc[3:-1])
        contents_article_1.append(content_article_1)
        contents_article_2.append(content_article_2)
        contents_article_3.append(content_article_3)

    news_df = pd.DataFrame({'title': titles, 'location': contents_loc, 'article1': contents_article_1, 'article2': contents_article_2,
                            'article3': contents_article_3, 'date': postdate})
    news_df.to_csv('blog_' + keyword + '.csv', index=False, encoding='utf-8-sig')
    news_df = news_df.map(remove_special_characters)

    for index, row in news_df.iterrows():
        # 지정된 열들을 반복하며 첫 번째 공백이 아닌 값을 찾습니다.
        for column in columns_to_check:
            value = row[column]
            # 문자열로 변환 후, 공백을 제거하고 비어있지 않은지 확인합니다.
            if pd.notnull(value) and str(value).strip():
                # 공백이 아닌 값을 찾으면 새 열에 저장하고 반복을 중단합니다.
                news_df.at[index, 'article'] = value
                break

    news_df.drop(['article1', 'article2', 'article3'], axis=1, inplace=True)

    news_df.to_csv('blog_' + keyword + '_k.csv', encoding='utf-8-sig')
    news_df.to_csv('blog_' + keyword + '_cut.csv', encoding='utf-8-sig')


except:
    contents_loc.append('error')
    contents_article_1.append('error')
    contents_article_2.append('error')
    contents_article_3.append('error')

    news_df = pd.DataFrame({'title': titles, 'location': contents_loc, 'article1': contents_article_1, 'article2': contents_article_2,
                             'article3': contents_article_3, 'date': postdate})
    news_df.to_csv('blog_' + keyword + '.csv', index=False, encoding='utf-8-sig')
    news_df = news_df.map(remove_special_characters)

    for index, row in news_df.iterrows():
        # 지정된 열들을 반복하며 첫 번째 공백이 아닌 값을 찾습니다.
        for column in columns_to_check:
            value = row[column]
            # 문자열로 변환 후, 공백을 제거하고 비어있지 않은지 확인합니다.
            if pd.notnull(value) and str(value).strip():
                # 공백이 아닌 값을 찾으면 새 열에 저장하고 반복을 중단합니다.
                news_df.at[index, 'article'] = value
                break

    news_df.drop(['article1', 'article2', 'article3'], axis=1, inplace=True)

    news_df.to_csv('blog_' + keyword + '_k.csv', index=False, encoding='utf-8-sig')
    news_df.to_csv('blog_' + keyword + '_cut.csv', index=False, encoding='utf-8-sig')


