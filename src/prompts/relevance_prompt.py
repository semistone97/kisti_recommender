from langchain_core.prompts import PromptTemplate

# Prompt
reason_template = '''
당신은 데이터 과학자입니다. 아래는 연구 데이터 목록입니다.

각 데이터 혹은 논문 항목은 다음 컬럼을 가지고 있습니다:
- ID: 각 데이터의 고유키
- 제목
- 설명
- 키워드

[목표]
모든 항목에 대해 해당 항목의 선정 사유를 작성해 주세요.

**중요: relevant_id와 reason의 개수는 반드시 동일해야 합니다.**

[Input]
연구 주제: {title}
연구 설명: {description}
키워드: {keyword}

[Data]
데이터 목록:
{data}

[Output]
다음 형식의 JSON을 출력하세요. relevant_id와 reason의 길이가 정확히 일치해야 합니다:

{{
  "relevant_id": ["ID1", "ID2", "ID3"],
  "reason": ["이유1", "이유2", "이유3"]
}}
'''

reason_prompt = PromptTemplate.from_template(reason_template)
