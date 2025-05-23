# langchain_setup.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

title_prompt = ChatPromptTemplate.from_template(
    """You are an assistant that creates concise, meaningful titles.
Given the following conversation, create a short title (max 10 words) that summarizes the main topic:

{conversation}

Title:"""
)

llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", temperature=0.4)
chat_title = title_prompt | llm

