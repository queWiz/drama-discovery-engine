import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_chroma import Chroma
from langchain_core.documents import Document

# --- UPDATED IMPORTS HERE ---
# We use "app.database" instead of just ".database" 
# so Python knows exactly where to look from the root folder.
from app.database import SessionLocal
from app.models import Show

# Load environment variables (API Key)
load_dotenv()

# Setup Google's Embedding Model
# This converts text into a list of numbers (vectors)
# embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


# Define where to save the vector database locally
PERSIST_DIRECTORY = "./chroma_db"

def index_shows():
    """
    Reads shows from SQLite, creates embeddings, and saves to ChromaDB.
    """
    print("Starting vector indexing process...")
    db = SessionLocal()
    shows = db.query(Show).all()
    
    if not shows:
        print("No shows found in SQLite database. Run ingest_to_db.py first.")
        return

    documents = []
    for show in shows:
        # We combine title, genres, and synopsis into one block of text
        # This gives the AI the full context of the show.
        page_content = f"Title: {show.title}\nGenres: {', '.join(show.genres)}\nSynopsis: {show.synopsis}"
        
        # Create a LangChain Document object
        # We store metadata (id, title) so we can retrieve the specific show later
        doc = Document(
            page_content=page_content,
            metadata={"show_id": show.id, "title": show.title}
        )
        documents.append(doc)

    print(f"Prepared {len(documents)} documents for indexing.")

    # Create/Update the Vector Database
    # This automatically calls the Google API to get embeddings
    vector_db = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY
    )
    
    print("Vector database updated successfully!")
    db.close()

def get_vector_db():
    """Returns the existing Chroma vector database instance."""
    return Chroma(
        persist_directory=PERSIST_DIRECTORY, 
        embedding_function=embeddings
    )

if __name__ == "__main__":
    # Run this script directly to build the index
    index_shows()