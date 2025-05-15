import os
import json
import re
from django.conf import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY

llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", temperature=0.4)

prompt = PromptTemplate(
    input_variables=["company_name", "mission", "core_values", "culture_keywords"],
    template="""
You are an AI assessment builder. Generate 10 culture fit questions in JSON format based on the following EVP.

Company Name: {company_name}
Mission: {mission}
Core Values: {core_values}
Culture Keywords: {culture_keywords}

Return **only** a valid JSON array like this:
[
  {{
    "dimension": "Integrity",
    "statement": "I value being honest and transparent in decision-making."
  }},
  ...
]
Do not add explanations or markdown.
"""
)

# Chain: prompt → LLM
chain = prompt | llm

# Clean LLM output
def extract_valid_json(text: str):
    # Remove markdown code blocks, if present
    if text.startswith("```json") or text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text.strip())
        text = re.sub(r"```$", "", text.strip())
    # Find first JSON array in text
    match = re.search(r"\[\s*{.*}\s*\]", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    # Fallback if the whole output is a JSON array
    return json.loads(text)

def generate_questions_from_company(company):
    input_data = {
        "company_name": company.name,
        "mission": company.mission_statement,
        "core_values": ", ".join(company.core_values),
        "culture_keywords": ", ".join(company.culture_keywords),
    }

    result = chain.invoke(input_data)

    try:
        return extract_valid_json(result.content)
    except Exception as e:
        raise ValueError(f"Gemini returned invalid JSON: {e}")
