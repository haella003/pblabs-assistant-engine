import os
import fitz
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# We use a small, fast model for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
index = None
chunks = []

def build_knowledge_index(vault_path):
    global index, chunks
    raw_text = ""
    
    # 1. Extract text from all PDFs/TXTs
    for filename in os.listdir(vault_path):
        path = os.path.join(vault_path, filename)
        if filename.endswith(".pdf"):
            doc = fitz.open(path)
            raw_text += " ".join([page.get_text() for page in doc])
        elif filename.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                raw_text += f.read()

    # 2. Chunking: Split text into 500-character pieces
    # This ensures EDI gets specific context, not random pages
    size = 500
    chunks = [raw_text[i:i+size] for i in range(0, len(raw_text), size)]
    
    # 3. Create Embeddings
    if not chunks:
        print("Warning: No text chunks found. Is your knowledge_vault empty?")
        return

    embeddings = model.encode(chunks)
    
    # 4. Create FAISS Index
    # Force the dimension to be a plain integer
    dimension = int(embeddings.shape[1])
    
    global index
    index = faiss.IndexFlatL2(dimension)
    
    # Ensure the data is float32 (FAISS requirement)
    index.add(np.array(embeddings).astype('float32'))
    print(f"Knowledge Vault Indexed: {len(chunks)} chunks ready.")

def get_relevant_context(query, k=3):
    """Finds relevant chunks and forces a flat integer list to avoid errors."""
    global index, chunks
    if index is None or not chunks: 
        return ""

    # 1. Search
    query_vector = model.encode([query])
    distances, indices = index.search(np.array(query_vector).astype('float32'), k)

    # 2. THE NUCLEAR FLATTEN: 
    # .flatten() turns [] into
    # [int(i) for i in ...] ensures they are standard Python numbers
    try:
        flat_indices = [int(i) for i in indices.flatten()]
    except Exception as e:
        print(f"❌ Flattening error: {e}")
        return ""

    relevant_chunks = []
    for idx in flat_indices:
        # Now idx is guaranteed to be a single integer
        if idx != -1 and idx < len(chunks):
            relevant_chunks.append(chunks[idx])

    context = "\n".join(relevant_chunks)
    
    if context:
        print(f"✅ Librarian found {len(relevant_chunks)} chunks.")
    else:
        print("⚠️ Librarian found nothing.")
        
    return context