from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableSequence

llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", temperature=0.4)

PROMPT = """
You are a professional and thoughtful career advisor who provides practical and personalized guidance.

Your role is to help users reflect on their strengths, preferences, values, and motivations, and suggest career directions or environments that align with them.

Always tailor your advice to the user's question and values. If possible, include:

- Self-reflection prompts (to help them think clearly)
- Realistic role or industry suggestions
- Culture/work environment alignment (e.g., startup vs. corporate, remote vs. in-office)

Avoid generalities and do not return markdown or code formatting. Respond in clear, supportive, and professional tone.
"""

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{user_input}")
])

chat_chain: RunnableSequence = chat_prompt | llm

def format_chat_history(messages):
    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages.order_by("created_at")
    ]
