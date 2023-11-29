import pandas as pd
import requests


def get_lat_lng_from_address(address, api_key):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {
        "Authorization": f"KakaoAK {api_key}"
    }
    params = {"query": address}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        try:
            address_info = response.json()['documents'][0]['address']
            return address_info['y'], address_info['x']  # 위도, 경도
        except (IndexError, KeyError):

            return -1, -1

        else:
            return -1 , -1


csv = pd.read_csv('gonggong_seoul.csv', encoding='utf-8-sig')
csv['address'] = 0

pd.set_option('mode.chained_assignment',  None)
api_key = my-api-key-kakaomap

for i in range(len(csv)):
    address = csv['address'][i]
    latitude, longitude = get_lat_lng_from_address(address, api_key)
    csv['latitude'][i] = latitude
    csv['longitude'][i] = longitude
    print(i)

csv.to_csv('gonggong-seoul_1.csv', encoding='utf-8-sig', index=False)
