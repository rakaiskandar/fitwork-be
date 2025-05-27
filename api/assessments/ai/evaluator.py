import os, re
from django.conf import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence

# Load API key
os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY

# Initialize Gemini
llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", temperature=0.4)

# Build prompt for evaluation
prompt = PromptTemplate(
    input_variables=[
        "company_name", "mission", "core_values",
        "culture_keywords", "overall_score", "dimension_scores"
    ],
    template="""
You are an expert organizational psychologist and career coach.  
Given the following culture-fit assessment results, provide a concise evaluation report:

Company: {company_name}
Mission: {mission}
Core Values: {core_values}
Culture Keywords: {culture_keywords}

Assessment Results:
- Overall fit score: {overall_score} / 5
- Scores by dimension:
{dimension_scores}

Write a brief summary (2-3 paragraphs) interpreting these results, highlighting strengths and areas to watch.
"""
)

chain: RunnableSequence = prompt | llm

def evaluate_assessment(company, overall_score, dimension_scores):
    # Format the dimension scores as bullet lines
    dim_text = "\n".join(f"- {dim}: {score}/5" for dim, score in dimension_scores.items())

    inputs = {
        "company_name": company.name,
        "mission": company.mission_statement,
        "core_values": ", ".join(company.core_values),
        "culture_keywords": ", ".join(company.culture_keywords),
        "overall_score": overall_score,
        "dimension_scores": dim_text
    }

    result = chain.invoke(inputs)
    # strip any markdown or code fences
    text = re.sub(r"^```(?:txt|json)?\s*|\s*```$", "", result.content.strip())
    return text
