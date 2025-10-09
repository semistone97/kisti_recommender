
import xml.etree.ElementTree as ET
import pandas as pd
import os

# 현재 스크립트 파일의 디렉토리 경로를 기준으로 파일 경로 설정
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
file_path = os.path.join(__location__, "asdad.md")


# 파일 읽기
with open(file_path, 'r', encoding='utf-8') as f:
    # 첫 줄의 불필요한 주석 제거
    xml_content = f.read().splitlines()[1:]
    xml_content = '\n'.join(xml_content)

# XML 파싱
root = ET.fromstring(xml_content)

# recordList 찾기
record_list_element = root.find('recordList')

# 데이터를 담을 리스트
records = []

if record_list_element is not None:
    # 각 record에 대해 반복
    for record_element in record_list_element.findall('record'):
        record_data = {}
        # 각 item에 대해 반복
        for item_element in record_element.findall('item'):
            meta_code = item_element.get('metaCode')
            # CDATA 섹션의 텍스트 추출
            value = item_element.text.strip() if item_element.text else ''
            record_data[meta_code] = value
        records.append(record_data)

# DataFrame 생성
df = pd.DataFrame(records)

# 결과 출력
print(df)
