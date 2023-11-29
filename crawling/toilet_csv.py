import requests
import pandas as pd

def get_address_from_lat_lng(lat, lng, api_key):
    url = "https://dapi.kakao.com/v2/local/geo/coord2address.json"
    headers = {
        "Authorization": f"KakaoAK {api_key}"
    }
    params = {
        "x": lng,
        "y": lat,
        "input_coord": "WGS84"
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        try:
            address_info = response.json()['documents'][0]['address']
            return address_info['address_name']
        except (IndexError, KeyError):
            return "주소를 찾을 수 없습니다."
    else:
        return "API 요청 실패: " + str(response.status_code)

# 사용 예시
pd.set_option('mode.chained_assignment',  None)
api_key = my-api-key-kakomap
csv = pd.read_csv("gonggong_seoul.csv",  encoding='utf-8-sig',index_col=0)

csv['address'] = 0

for i in range(len(csv)):
    lat = csv['latitude'][i]
    log = csv['longitude'][i]
    address = get_address_from_lat_lng(lat, log, api_key)
    csv['address'][i] = address
    print(address)

csv.to_csv("gonggong_seoul_1.csv", encoding='utf-8-sig', index=False)
