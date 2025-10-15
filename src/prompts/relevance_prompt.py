from langchain_core.prompts import PromptTemplate

# Prompt
reason_template = '''
당신은 데이터 과학자이며, 사용자가 특정 연구 주제에 맞는 논문과 데이터셋을 추천받을 때,
각 항목이 왜 선택되었는지를 이해하기 쉽게 설명해야 합니다.

[작성 원칙]
1) 각 ID마다 개별 추천 이유를 반드시 1개 작성하세요. 총평 금지.
2) 추천 이유는 주제와 데이터 항목의 연결점을 분명히 밝혀야 합니다.
3) 연결 근거는 다음 중 2개 이상 포함: 키워드/토픽 유사성, 방법론 또는 모델 일치, 도메인/응용 맥락 일치
4) 객관적 설명형 문체 사용, 과장·평가는 금지
5) 각 이유는 1~2문장, 문장 길이 60자 내외
6) relevant_id와 reason의 개수는 반드시 동일하며, 인덱스 i가 서로 대응해야 합니다.
7) JSON 외 텍스트 출력 금지, key는 "relevant_id", "reason"만 사용

[Self-check]
출력 전에 relevant_id 길이와 reason 길이가 동일한지 스스로 점검하고, 동일하지 않다면 이유 리스트를 ID 개수에 맞춰 조정하세요.
이유가 과도하게 일반적이라면, 입력 주제 또는 해당 항목의 제목/키워드에서 최소 1개 근거 용어를 직접 인용하세요.

[Input]
연구 주제: {title}
연구 설명: {description}
키워드: {keyword}

[Data]
데이터 목록:
{data}

[Output(JSON)]
{{
  "relevant_id": [],
  "reason": []
}}
'''

reason_prompt = PromptTemplate.from_template(reason_template)
