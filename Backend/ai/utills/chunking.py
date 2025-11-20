from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunking(text):
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)
    print(f"Total chunks created: {len(chunks)}")
    return chunks