import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import errors

# Load .env from parent directory
load_dotenv("../../../.env")
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API Key is missing in .env")
    sys.exit(1)

client = genai.Client(api_key=api_key)

print("🔍 1. 테스트: 일반 텍스트 모델 (gemini-2.0-flash)")
try:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Hello, this is a test. Reply with 'OK' if you can read this."
    )
    print(f"✅ 텍스트 모델 성공: {response.text}")
except errors.APIError as e:
    print(f"❌ 텍스트 모델 실패 (API Error): {e}")
except Exception as e:
    print(f"❌ 텍스트 모델 실패 (Other Error): {e}")
