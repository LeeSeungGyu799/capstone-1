import json
import re
import pandas as pd


def find_first_alpha(text):
    match = re.search("[a-zA-Z]", text)
    if match is None:
        return -1
    first = match.group()
    if match:
        return first
    else:
        return None


def find_last_alpha(text):
    text = text[::-1]
    match = re.search("[a-zA-Z]", text)
    if match is None:
        return -1
    last = match.group()
    if match:
        return last
    else:
        return None


result = []
s_list = []
loc_list = []

with open('blog_서울 스타벅스 장애인 화장실.json', 'r', encoding='utf-8-sig') as f:
    json_data = json.load(f)
with open('starbucks_name.txt', 'r', encoding='utf-8-sig') as starbucks:
    s_list = starbucks.readlines()
    s_list = [line.strip() for line in s_list]

for i in range(len(json_data)):
    output_t = json_data[i][0]['output']
    check_star = find_first_alpha(output_t)
    check = find_last_alpha(output_t)
    if check_star == 'y' or check_star == 'Y':
        if check == 'y' or check == 'Y':
            if json_data[i][0]['loc'] != "nan":
                if '스타벅스' in json_data[i][0]['loc']:
                    if json_data[i][0]['loc'].split()[1] in s_list:
                        loc_list.append(json_data[i][0]['loc'])

            else:
                place = json_data[i][0]['output'].split(':')[2].split('\n')[0].replace(' ', '')
                if place in s_list:
                    loc_list.append('스타벅스 ' + place)

loc_list = list(set(loc_list))

csv = pd.read_csv('starbucks_crawl.csv', encoding='utf-8-sig')

for i in range(len(loc_list)):
    csv.loc[csv['name'] == loc_list[i], 'disabled_man'] = 1
    csv.loc[csv['name'] == loc_list[i], 'disabled_woman'] = 1
    #csv.loc[csv['name'] == loc_list[i], 'diaper'] = 1

csv.to_csv('starbucks_crawl.csv', encoding='utf-8-sig', index=False)







print(loc_list)
            #result.append(json_data[i])

#with open("test.json", "w", encoding='utf-8-sig') as fw:
        #json.dump(result, fw, ensure_ascii=False, indent='\t')





