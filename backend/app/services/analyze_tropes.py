import google.generativeai as genai
import os
import json
import time
from dotenv import load_dotenv
from app.database import SessionLocal
from app.models import Show

# Load API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Use the fast, smart model
model = genai.GenerativeModel('gemini-2.5-flash')

def clean_ai_response(text):
    """
    Helper to strip markdown code blocks if the AI adds them.
    e.g. ```json ["Trope"] ``` -> ["Trope"]
    """
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def analyze_tropes():
    print("🕵️ Starting Trope Hunt...")
    db = SessionLocal()
    
    # Get all shows that have reviews but NO tropes yet
    # This allows you to stop/start the script without re-doing work
    shows = db.query(Show).filter(Show.reviews.isnot(None)).all()
    
    print(f"Found {len(shows)} shows to analyze.")
    
    count = 0
    for show in shows:
        # If we already analyzed it, skip (unless you want to force re-run)
        if show.tropes: 
            continue

        print(f"[{count+1}/{len(shows)}] Analyzing: {show.title}...")
        
        # Construct the context for the AI
        # We combine Synopsis (Official info) + Reviews (User info)
        prompt = f"""
        Analyze the K-Drama "{show.title}".
        
        DATA:
        - Synopsis: {show.synopsis}
        - Official Rating: {show.rating}/10
        - User Reviews: {show.reviews[:3000]}
        
        TASK 1: Identify Top 5 specific narrative tropes (e.g. Slow Burn, Revenge).
        
        TASK 2: Determine if this show is "Underrated", "Overrated", or "Rated Fairly".
        - Underrated: Rating is low (< 8.2) but reviews are glowing/passionate.
        - Overrated: Rating is high (> 8.7) but reviews complain about plot holes/boring.
        - Rated Fairly: Reviews match the score.
        
        RETURN JSON ONLY:
        {{
            "tropes": ["string", "string"],
            "verdict": "Underrated" | "Overrated" | "Rated Fairly"
        }}
        """
        
        try:
            # Ask Gemini
            response = model.generate_content(prompt)
            
            cleaned_text = clean_ai_response(response.text)
            data = json.loads(cleaned_text)
            
            # Save BOTH to DB
            show.tropes = data.get("tropes", [])
            show.verdict = data.get("verdict", "Rated Fairly")
            
            db.commit()
            print(f"   -> {show.title}: {show.verdict} | {show.tropes}")
            
            # Rate Limit Protection (Sleep a tiny bit)
            time.sleep(4)
            count += 1
            
        except Exception as e:
            print(f"   ❌ Error analyzing {show.title}: {e}")
            continue

    print("🎉 Trope Analysis Complete!")
    db.close()

if __name__ == "__main__":
    analyze_tropes()