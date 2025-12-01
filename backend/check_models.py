import os
from dotenv import load_dotenv
import google.generativeai as genai

# 1. Load the API Key from your .env file
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found. Check your .env file.")
    exit(1)

print(f"🔑 Found API Key: {api_key[:5]}...{api_key[-5:]}")

# 2. Configure the Google Library
genai.configure(api_key=api_key)

print("\n📡 Connecting to Google servers to list available models...")

try:
    # 3. List all models available to this key
    found_any = False
    for m in genai.list_models():
        # We only care about models that can generate text (generateContent)
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ AVAILABLE: {m.name}")
            found_any = True
    
    if not found_any:
        print("⚠️  No text-generation models found. You might need to enable the API in Google Cloud Console.")

except Exception as e:
    print(f"\n❌ Error connecting to Google: {e}")
    print("Tip: Check if your API Key is valid and if 'Generative Language API' is enabled in Google Cloud Console.")