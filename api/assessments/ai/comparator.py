import os, re
from django.conf import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence

# Load your API key
os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY

# Initialize the Gemini model
llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", temperature=0.4)

# Prompt template for comparison
prompt = PromptTemplate(
    input_variables=[
        "company1", "overall1", "dim1",
        "company2", "overall2", "dim2"
    ],
    template="""
You are an expert organizational psychologist. Compare two culture-fit assessment sessions:

Session A - Company: {company1}
Overall Score A: {overall1}/5
Dimension Scores A:
{dim1}

Session B - Company: {company2}
Overall Score B: {overall2}/5
Dimension Scores B:
{dim2}

Provide a concise comparative analysis (2-3 paragraphs), highlighting which company the user fits better, strengths, and areas to improve in each context. Do not include numeric tables or code.
"""
)

# Chain them
chain: RunnableSequence = prompt | llm

def evaluate_comparison(a, b):
    """
    a, b are dicts with keys:
      - company, overall_score, dimension_scores (dict)
    """
    dim1_text = "\n".join(f"- {dim}: {score}/5" for dim,score in a["dimension_scores"].items())
    dim2_text = "\n".join(f"- {dim}: {score}/5" for dim,score in b["dimension_scores"].items())

    inputs = {
        "company1": a["company"],
        "overall1": a["overall_score"],
        "dim1": dim1_text,
        "company2": b["company"],
        "overall2": b["overall_score"],
        "dim2": dim2_text,
    }

    resp = chain.invoke(inputs)
    # strip markdown fences
    text = re.sub(r"^```(?:txt)?", "", resp.content).strip()
    text = re.sub(r"```$", "", text).strip()
    return text
