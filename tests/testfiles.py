import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from .env
load_dotenv()
api_key = os.getenv("GEMINI_KEY")

# Configure the API
genai.configure(api_key=api_key)

# Create a model
model = genai.GenerativeModel("gemini-2.5-flash")

# Generate content
response = model.generate_content("Explain how AI works in a few words")
print(response.text)

