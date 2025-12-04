import os
import time
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from ..database import SessionLocal
from ..models import Show

load_dotenv()

# We use the newer 'text-embedding-004' model. 
# It is better and sometimes has separate quota buckets.
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

PERSIST_DIRECTORY = "chroma_db"

def get_vector_db():
    return Chroma(
        persist_directory=PERSIST_DIRECTORY, 
        embedding_function=embeddings
    )

def index_shows():
    print("Starting vector indexing process...")
    db = SessionLocal()
    shows = db.query(Show).all()
    
    if not shows:
        print("No shows found in SQLite database.")
        return

    documents = []
    for show in shows:
        safe_tropes = show.tropes if show.tropes else []
        safe_tags = show.tags if show.tags else []
        tropes_str = ", ".join(safe_tropes)
        tags_str = ", ".join(safe_tags)
        
        page_content = f"""
        Title: {show.title}
        Year: {show.year} 
        Genres: {', '.join(show.genres)}
        Tags: {tags_str}
        Tropes: {tropes_str}
        Verdict: {show.verdict}
        Synopsis: {show.synopsis}
        """
        
        doc = Document(
            page_content=page_content,
            metadata={
                "show_id": show.id, 
                "title": show.title,
                "image_url": show.image_url or "",
                "rating": show.rating or 0.0,
                "year": show.year or 0,
                "verdict": show.verdict or "Rated Fairly",
                "synopsis": show.synopsis or "No synopsis.",
                "tropes_str": tropes_str,
                "tags_str": tags_str
            }
        )
        documents.append(doc)

    print(f"Prepared {len(documents)} documents.")

    # --- BULLETPROOF BATCH PROCESSING ---
    # We process 5 docs at a time.
    # If we hit an error, we wait 60s and RETRY the SAME batch.
    
    batch_size = 5 # Reduced to 5 to be safer
    total_docs = len(documents)
    
    vector_db = None
    
    print("🚀 Starting Resilient Indexing...")
    
    for i in range(0, total_docs, batch_size):
        batch = documents[i : i + batch_size]
        
        # Retry Loop: Keep trying this batch until success
        while True:
            try:
                print(f"   Processing batch {i} to {i + batch_size}...")
                
                if i == 0 and vector_db is None:
                    # First batch creates the collection
                    vector_db = Chroma.from_documents(
                        documents=batch,
                        embedding=embeddings,
                        persist_directory=PERSIST_DIRECTORY
                    )
                else:
                    # Load existing if we crashed and restarted logic, or just add
                    if vector_db is None:
                         vector_db = Chroma(
                            persist_directory=PERSIST_DIRECTORY, 
                            embedding_function=embeddings
                        )
                    vector_db.add_documents(documents=batch)
                
                print("   ✅ Batch saved.")
                # Success! Break the retry loop and move to next for-loop iteration
                time.sleep(5) # Small cooldown between successful batches
                break 
                
            except Exception as e:
                print(f"   ⚠️ Rate Limit Hit (429). Cooling down for 60s...")
                print(f"   (Error: {e})")
                time.sleep(60) # Wait 1 minute then loop back and try AGAIN
                continue

    print("🎉 Vector database updated successfully!")
    db.close()

if __name__ == "__main__":
    index_shows()

# LOCAL VERSION

# import os
# from dotenv import load_dotenv
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_chroma import Chroma
# from langchain_core.documents import Document
# # Fix import to prevent circular dependency if any, though relative imports usually work
# from ..database import SessionLocal
# from ..models import Show

# load_dotenv()

# # Global variable to cache the model after loading
# _embeddings_instance = None

# def get_embeddings():
#     """
#     Lazy-load the embedding model.
#     This prevents the server from crashing on startup due to timeouts.
#     The model will only download/load when the first request comes in.
#     """
#     global _embeddings_instance
#     if _embeddings_instance is None:
#         print("⏳ Loading AI Model (Lazy Load)...")
#         _embeddings_instance = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#         print("✅ AI Model Loaded.")
#     return _embeddings_instance

# PERSIST_DIRECTORY = "chroma_db" # Ensure path is relative for cloud

# def index_shows():
#     """
#     Reads shows from SQLite, creates embeddings, and saves to ChromaDB.
#     """
#     print("Starting vector indexing process...")
#     db = SessionLocal()
#     shows = db.query(Show).all()
    
#     if not shows:
#         print("No shows found in SQLite database.")
#         return

#     documents = []
#     for show in shows:
#         # Construct the rich context
#         safe_tropes = show.tropes if show.tropes else []
#         safe_tags = show.tags if show.tags else []
#         tropes_str = ", ".join(safe_tropes)
#         tags_str = ", ".join(safe_tags)
        
#         page_content = f"""
#         Title: {show.title}
#         Year: {show.year} 
#         Genres: {', '.join(show.genres)}
#         Tags: {tags_str}
#         Tropes: {tropes_str}
#         Verdict: {show.verdict}
#         Synopsis: {show.synopsis}
#         """
        
#         doc = Document(
#             page_content=page_content,
#             metadata={
#                 "show_id": show.id, 
#                 "title": show.title,
#                 "image_url": show.image_url or "",
#                 "rating": show.rating or 0.0,
#                 "year": show.year or 0,
#                 "verdict": show.verdict or "Rated Fairly",
#                 "synopsis": show.synopsis or "No synopsis.",
#                 "tropes_str": tropes_str,
#                 "tags_str": tags_str
#             }
#         )
#         documents.append(doc)

#     print(f"Prepared {len(documents)} documents for indexing.")

#     # Create/Update the Vector Database
#     # Note: We call get_embeddings() here, executing the load
#     vector_db = Chroma.from_documents(
#         documents=documents,
#         embedding=get_embeddings(), 
#         persist_directory=PERSIST_DIRECTORY
#     )
    
#     print("Vector database updated successfully!")
#     db.close()

# def get_vector_db():
#     """Returns the existing Chroma vector database instance."""
#     return Chroma(
#         persist_directory=PERSIST_DIRECTORY, 
#         embedding_function=get_embeddings() # Lazy load here too
#     )

# if __name__ == "__main__":
#     index_shows()

# # import os
# # from dotenv import load_dotenv
# # from langchain_huggingface import HuggingFaceEmbeddings 
# # from langchain_chroma import Chroma
# # from langchain_core.documents import Document

# # # --- UPDATED IMPORTS HERE ---
# # # We use "app.database" instead of just ".database" 
# # # so Python knows exactly where to look from the root folder.
# # from app.database import SessionLocal
# # from app.models import Show

# # # Load environment variables (API Key)
# # load_dotenv()

# # # Setup Google's Embedding Model
# # # This converts text into a list of numbers (vectors)
# # # embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
# # embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


# # # Define where to save the vector database locally
# # PERSIST_DIRECTORY = "./chroma_db"

# # def index_shows():
# #     """
# #     Reads shows from SQLite, creates embeddings, and saves to ChromaDB.
# #     """
# #     print("Starting vector indexing process...")
# #     db = SessionLocal()
# #     shows = db.query(Show).all()
    
# #     if not shows:
# #         print("No shows found in SQLite database. Run ingest_to_db.py first.")
# #         return

# #     documents = []
# #     for show in shows:
# #         # Ensure tropes/tags are lists before joining (handling None cases)
# #         safe_tropes = show.tropes if show.tropes else []
# #         safe_tags = show.tags if show.tags else []

# #         tropes_str = ", ".join(safe_tropes)
# #         tags_str = ", ".join(safe_tags)

# #         # We combine title, genres, and synopsis into one block of text
# #         # This gives the AI the full context of the show.
# #         # We now include the AI-detected tropes in the vector embedding!
# #         # This makes the search engine MUCH smarter.
# #         page_content = f"""
# #         Title: {show.title}
# #         Year: {show.year} 
# #         Genres: {', '.join(show.genres)}
# #         Tags: {', '.join(show.tags)}
# #         Tropes: {tropes_str}
# #         Verdict: {show.verdict}
# #         Synopsis: {show.synopsis}
# #         """
        
# #         # Create a LangChain Document object
# #         # We store metadata (id, title) so we can retrieve the specific show later
# #         doc = Document(
# #             page_content=page_content,
# #             metadata={
# #                 "show_id": show.id, 
# #                 "title": show.title,
# #                 "image_url": show.image_url or "",
# #                 "rating": show.rating or 0.0,
# #                 "year": show.year or 0,
# #                 "verdict": show.verdict or "Rated Fairly",
# #                 "synopsis": show.synopsis or "No synopsis available.",
# #                 "tropes_str": tropes_str, # Stored as comma-separated string
# #                 "tags_str": tags_str
# #             }
# #         )
# #         documents.append(doc)

# #     print(f"Prepared {len(documents)} documents for indexing.")

# #     # Create/Update the Vector Database
# #     # This automatically calls the Google API to get embeddings
# #     vector_db = Chroma.from_documents(
# #         documents=documents,
# #         embedding=embeddings,
# #         persist_directory=PERSIST_DIRECTORY
# #     )
    
# #     print("Vector database updated successfully!")
# #     db.close()

# # def get_vector_db():
# #     """Returns the existing Chroma vector database instance."""
# #     return Chroma(
# #         persist_directory=PERSIST_DIRECTORY, 
# #         embedding_function=embeddings
# #     )

# # if __name__ == "__main__":
# #     # Run this script directly to build the index
# #     index_shows()