# backend/app/chat_service.py
import os
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.chains import create_retrieval_chain
# from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from .vector_store import get_vector_db

# Initialize the LLM (The Brain)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

def get_chat_response(
    user_query: str, 
    genre: str | None = None,
    rating: int = 0,
    year: str | None = None,
    trope: str | None = None
):
    # 1. Get our Vector DB
    vector_db = get_vector_db()
    
    # 2. Create a "Retriever"
    # It will find the top 5 most relevant shows for the query
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})

    # --- HYBRID SEARCH LOGIC ---
    # If a genre is selected, we force the AI to pay attention to it.
    system_instruction = (
        "You are an expert K-drama assistant. "
        "Use the provided context to recommend shows. "
    )

    constraints = []
    
    if genre and genre != "All":
        constraints.append(f"- Genre: Must be '{genre}'.")
        # Augment query for better vector matching
        user_query = f"{genre} drama. {user_query}"
        
    if rating > 0:
        constraints.append(f"- Minimum Rating: {rating}/10.")
        
    if year and year != "All":
        if year == "2020+": constraints.append("- Era: Released 2020 or later.")
        elif year == "Classic": constraints.append("- Era: Released before 2015.")
        else: constraints.append(f"- Era: {year}")

    if trope:
        constraints.append(f"- Mandatory Theme/Trope: {trope}.")
        user_query = f"{trope}. {user_query}"

    if constraints:
        system_instruction += "\n\nSTRICT CONSTRAINTS:\n" + "\n".join(constraints)

    # 3. Define the System Prompt
    # This instructs the AI on how to behave.
    system_prompt = (
        f"{system_instruction}"
        "You are an expert anime and K-drama recommender assistant. "
        "Use the following pieces of retrieved context to answer the user's question. "
        "If the context doesn't contain the answer, say you don't know, do not make things up. "
        "Always recommend specific shows from the context if they fit."
        "\n\n"
        "{context}"
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    # 4. Create the Chain (The Pipeline)
    # This connects: Retriever -> Prompt -> LLM
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    # 5. Run the chain
    response = rag_chain.invoke({"input": user_query})

    # Extract sources from the AI's context
    sources = [doc.metadata for doc in response["context"]]

    # CRITICAL: Return a dictionary with 'answer' and 'sources'
    return {
        "answer": response["answer"],
        "sources": sources
    }
    
