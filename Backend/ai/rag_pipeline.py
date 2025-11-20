import os
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.tools import Tool
from config.setting import GOOGLE_API_KEY, GOOGLE_API_KEY1
from ai.utills.search import search
from ai.prompts.system_prompts import system_prompt
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI  
from db.save_in_database import save_sessions_in_mongo     
from db.database import sessions 
from langchain_community.chat_message_histories import RedisChatMessageHistory
from config.redis_config import redis_client    
from dotenv import load_dotenv
load_dotenv()

# from ai.prompts import system_prompts

 
#  Setting llm 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(
    model="gpt-4.1",     # or "gpt-4.1-mini", etc.
    temperature=0.2,
    api_key=OPENAI_API_KEY
)
tool = Tool(
    name="search",
    description="This is simple search tool to search in the vector database to extracct relevatn information from the document according to user querry. Its input should be string querry",
    func=search
)

agent = create_react_agent(
    model=model,
    tools=[tool]
    )


# config = 




# def rag_pipeline(query: str, user_id, session_id ):
async def rag_pipeline(userID: str, session_id: str, query: str , agents = agent, system_prompt=system_prompt):
    try:
        
        history = RedisChatMessageHistory(redis_client=redis_client, session_id=session_id)
        
        past_messages = await history.aget_messages()  # List[BaseMessage]
        
        messages = [SystemMessage(content=system_prompt)]
        
        for msg in past_messages:
            messages.append(msg)
            
        user_msg = HumanMessage(content=query)    
        
        messages.append(user_msg)
        response = await agents.ainvoke({"messages": messages})
        # print(f"This is response : {response}")
      
        # ai_response = response["output"]

        # Save the conversation in Redis
        history.add_message(user_msg)          # Save user message
        
        
        # Suppose 'response' is what you printed
        # messags = list(response["messages"])
        
        messags = response.get("messages", [])
        
        for msg in reversed(messags):
            if isinstance(msg, AIMessage):
                queryResponse = msg.content
                history.add_message(AIMessage(content=queryResponse))  # Save AI response
                print("AIMessage found in contenxt:", queryResponse)
                return {"answer": queryResponse}

    except Exception as e:
        return {"answer": f"Error found : f {e}"}

