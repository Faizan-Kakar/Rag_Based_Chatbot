from config.pinecone_config import index
from langchain_core.tools import Tool


def search(querry : str , top_k : int = 3):
    results = index.search(
        namespace="chatbot",
        query={
            "top_k": top_k,
            "inputs": {
                'text': querry
            }
        }
    )
    return results