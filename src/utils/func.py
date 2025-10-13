import xml.etree.ElementTree as ET
import pandas as pd
import json

def xml_to_df(xml):
    # XML 파싱
    root = ET.fromstring(xml)

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

    df = pd.DataFrame(records)
    return df

def transform_query(input_query):

    query = {
        "BI": input_query,  # 전체
        # "TI": None,  # 논문명
        # "AU": None,  # 저자
        # "AB": None,  # 초록
        # "KW": None,  # 키워드
        # "PB": None,  # 출판사(발행기관)
        # "SN": None,  # ISSN
        # "BN": None,  # ISBN
        # "PY": None,  # 발행년도
        # "CN": None,  # 문헌번호
        # "DI": None   # DOI
    }

    json_query = json.dumps(query, separators=(',', ':')) 

    return json_query