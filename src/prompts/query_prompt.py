from langchain_core.prompts import PromptTemplate

# Prompt
query_template = '''
Generate search queries to find the most semantically relevant papers and datasets based on the given title, description and keywords.

[Search Engine Constraints]
- The search is exact-match based.
- Keep queries short and cohesive.
- Each query should consist of 2–3 words, preferably a combination of proper nouns or technical topics.

[Generation Procedure]
1. Identify Core Keywords: Summarize the main objects, methodology, domain, and application context of the research topic in one sentence.
2. Generate Candidates: Tentatively generate 8–10 query candidates, each with 2–3 words.
3. Apply Filtering Rules:
    - Remove generic, overly broad, or ambiguous expressions (e.g., “AI model”, “data analysis”).
    - Keep a balanced mix — 12 method-centered, 12 domain-centered, and 1–2 application-scenario-centered queries.
    - Exclude entries consisting only of abbreviations, but allow widely used ones (e.g., “BERT” is allowed, “ML” alone is not).
    - Do not use hyphens, special characters, or quotation marks.
4. Final Selection: Retain only the top 3–5.

[Prohibitions]
- Single-word queries are not allowed.
- Queries longer than 4 words are not allowed.
- Do not leave only stopword combinations (e.g., “for research”).
- Do not violate the JSON schema.

[Input]
- Research Topic: {title}
- Research Description: {description}
- Keywords: {keyword}

[Output]
Output in the following JSON format:

{{
"query": []
}}
'''

query_prompt = PromptTemplate.from_template(query_template)
