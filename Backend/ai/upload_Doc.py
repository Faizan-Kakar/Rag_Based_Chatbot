import os 
import pypdf
from config.pinecone_config import index
from ai.utills.chunking import chunking

base_path = os.path.dirname(__file__)
file_path = os.path.join(base_path, "Manual.pdf")


import uuid

def upload_Doc(file):
    
    # Loading and extracting text from PDF
    file = pypdf.PdfReader(file)
    text = ""   
    for page in file.pages:
        text += page.extract_text()
    
    # Chunking the text
    chunks = chunking(text)
    
    # Generate a unique ID for this document upload
    unique_id = str(uuid.uuid4())
    
    # Embedding and storing the chunks in Pinecone
    vectors = []
    for i, chunk in enumerate(chunks):
        unique_id = str(uuid.uuid4().hex)
        vectors.append({
            
            "id": f"doc1-chunk-{i}-{unique_id}",
            "text": chunk,   # ✅ raw text goes here
            "doc_id": "doc1",
            "doc_title": "manual",
            "chunk_number": str(i+1)
            
        })
        
    
    try:
        index.upsert_records("chatbot" , vectors)
        return "Upserted successfully"
    except Exception as e:
        return f"An error occurred while upserting to Pinecone: {e}"
   
 
