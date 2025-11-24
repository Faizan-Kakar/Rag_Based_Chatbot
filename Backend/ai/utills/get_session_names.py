from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
# Initialize the LLM once (reuse for efficiency)
llm = ChatOpenAI(model="gpt-4.1", temperature=0.2, api_key=OPENAI_API_KEY)

async def get_session_name(first_query: str) -> str:
    """
    Generate a session name based on the user's first query.
    
    Args:
        first_query (str): The first question/query asked by the user.
    
    Returns:
        str: A short and meaningful session name.
    """
    prompt = f"""
    You are an assistant that generates short and clear session names.
    The name should summarize the topic of the chat in 2-4 words.
    Example:
    - "What is JWT?" -> "JWT Basics"
    - "Explain neural networks" -> "Neural Networks"
    - "How to deploy FastAPI on AWS?" -> "FastAPI Deployment"
    
    First Query: "{first_query}"
    Session Name:
    """

    response = await llm.ainvoke(prompt)
    session_name = response.content.strip()
    
    return session_name
