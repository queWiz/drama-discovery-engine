import os, random
from langchain_google_genai import ChatGoogleGenerativeAI
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
    trope: str | None = None,
    watched_history: list[str] = []
):
    # 1. Get our Vector DB
    vector_db = get_vector_db()

    # --- QUERY AUGMENTATION (The Secret Sauce) ---
    # If the user has a history, we want the Vector Search to find things SIMILAR to it.
    # We pick up to 10 random shows from their list and add them to the query "behind the scenes".
    search_query = user_query

    if watched_history and len(watched_history) > 0:
        # Pick 5 random shows to influence the search
        samples = random.sample(watched_history, min(5, len(watched_history)))
        sample_str = ", ".join(samples)
        
        # We append this to the query sent to Chroma, but NOT the one sent to Gemini (to avoid confusion)
        # This forces the database to pull up shows that are semantically similar to what they watched.
        search_query = f"{user_query}. Similar to: {sample_str}"
    
    # 2. Create a "Retriever"
    # It will find the top 5 most relevant shows for the query
    retriever = vector_db.as_retriever(search_kwargs={"k": 8})

    # --- HYBRID SEARCH LOGIC ---
    # If a genre is selected, we force the AI to pay attention to it.
    system_instruction = (
        "You are an expert K-drama curator. "
        "Your goal is to recommend shows based on the user's request and their unique Taste Profile. "
    )

    constraints = []

    # Handle Watchlist (The Logic Flip)
    if watched_history:
        # We limit to the first 50 titles to save context window space
        history_str = ", ".join(watched_history[:50])
        
        system_instruction += (
            f"\n\nUSER TASTE PROFILE:"
            f"\nThe user has watched and liked the following shows: [{history_str}]."
            f"\nAnalyze the themes, genres, and vibes of these shows to understand their taste."
        )
        
        constraints.append("Do NOT recommend any show listed in the User Taste Profile (they have already seen them).")
    
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

    # Note: We can't use the simple 'create_retrieval_chain' anymore because 
    # we want to pass a DIFFERENT query to the retriever vs the LLM.
    # So we do it manually in 2 steps:
    
    # Step A: Retrieve docs using the AUGMENTED query
    docs = retriever.invoke(search_query)
    
    # Step B: Generate answer using the ORIGINAL query + Retrieved Docs
    response = question_answer_chain.invoke({
        "input": user_query,
        "context": docs
    })

    # rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    # response = rag_chain.invoke({"input": user_query})

    # Extract sources from the AI's context
    # sources = [doc.metadata for doc in response["context"]]
    sources = [doc.metadata for doc in docs]

    # Clean up sources (Deduping based on title)
    unique_sources = []
    seen = set()
    for s in sources:
        if s['title'] not in seen:
            unique_sources.append(s)
            seen.add(s['title'])

    # CRITICAL: Return a dictionary with 'answer' and 'sources'
    return {
        "answer": response,
        "sources": unique_sources
    }
    
