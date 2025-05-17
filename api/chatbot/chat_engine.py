from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableSequence

llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly and thoughtful career advisor helping users find ideal career paths aligned with their values."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{user_input}")
])

chat_chain: RunnableSequence = chat_prompt | llm

def format_chat_history(messages):
    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages.order_by("created_at")
    ]
