from langchain_core.prompts import PromptTemplate

# Prompt
reason_template = '''
You are a data scientist. Your task is to explain clearly why each listed paper or dataset
was selected for recommendation, so that users can easily understand the reasoning.

[Writing Guidelines]
1) You must provide exactly one explanation for each ID. Do not give overall summaries.
2) Each reason must explicitly describe the connection between the research topic and the data item.
3) Each reason should include at least two of the following elements:  
  - Keyword or topical similarity
  - Alignment in methodology or model
  - Match in domain or application context
4) Use an objective, descriptive tone. Avoid exaggeration or subjective evaluation.
5) Each reason should be 1–2 sentences long, about 60 words or fewer.
6) The number of items in "relevant_id" and "reason" must be identical, and the index i of each list must correspond to the same item.
7) Do not output any text other than JSON, and use only the keys "relevant_id" and "reason".

[Self-check]
Before finalizing your output, verify that the lengths of "relevant_id" and "reason" are equal.
If they differ, adjust the list of reasons to match the number of IDs.
If a reason sounds too generic, directly reference at least one supporting term
from the input topic, or from that item’s title or keywords.

[Input]
Research Topic: {title}
Research Description: {description}
Keywords: {keyword}

[Data]
Data list:
{data}

[Output(JSON)]
{{
  "relevant_id": [],
  "reason": []
}}
'''

reason_prompt = PromptTemplate.from_template(reason_template)
