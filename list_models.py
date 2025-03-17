import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API
API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=API_KEY)

# List available models
print("Available models:")
for model in genai.list_models():
    print(f"- {model.name}")
    print(f"  • Supported generation methods: {model.supported_generation_methods}")
    print()