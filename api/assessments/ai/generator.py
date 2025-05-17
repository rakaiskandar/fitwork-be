import os
import json
import re
from django.conf import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from api.companies.models import Company

# Load Gemini key
os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY

# LLM setup
llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", temperature=0.4)

# Prompt
assessment_prompt = PromptTemplate(
    input_variables=["company_name", "mission", "core_values", "culture_keywords"],
    template="""
You are a Culture-Fit Assessment Designer with 10+ years of experience in HR and organizational psychology. 
Generate 10 Likert-scale statements to assess a candidate's cultural fit with the company's values and environment.
Each question must be a statement rated 1-5 (1 = Strongly Disagree; 5 = Strongly Agree). 

Company Name: {company_name}
Mission: {mission}
Core Values: {core_values}
Culture Keywords: {culture_keywords}

Return ONLY a valid JSON array using this format:
[
  {{
    "dimension": "Integrity",
    "statement": "I value being transparent and honest in decision-making.",
    "scale": "Likert"
  }},
  ...
]

Avoid markdown, explanations, or code blocks. Only return valid JSON.
"""
)

# Prompt → LLM Chain
chain: RunnableSequence = assessment_prompt | llm

def extract_valid_json(text: str):
    # Remove code blocks if present
    text = re.sub(r"^```(json)?", "", text.strip())
    text = re.sub(r"```$", "", text.strip())

    # Attempt to extract clean JSON array
    match = re.search(r"\[\s*{.*}\s*\]", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    
    # Fallback
    return json.loads(text)

def generate_questions_from_company(company: Company) -> list[dict]:
    input_data = {
        "company_name": company.name,
        "mission": company.mission_statement,
        "core_values": ", ".join(company.core_values or []),
        "culture_keywords": ", ".join(company.culture_keywords or [])
    }

    response = chain.invoke(input_data)

    try:
        return extract_valid_json(response.content)
    except Exception as e:
        raise ValueError(f"Gemini returned invalid JSON: {e}")
