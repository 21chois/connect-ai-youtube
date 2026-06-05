import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API Key is missing.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

print("🔍 1. 테스트: 일반 텍스트 모델 (gemini-2.5-flash)")
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello, this is a test. Reply with 'OK' if you can read this."
    )
    print(f"✅ 텍스트 모델 성공: {response.text}")
except errors.APIError as e:
    print(f"❌ 텍스트 모델 실패 (API Error): {e}")
except Exception as e:
    print(f"❌ 텍스트 모델 실패 (Other Error): {e}")

print("\n🔍 2. 테스트: 비디오 생성 모델 (veo-3.1-generate-preview) 요청 시도")
try:
    op = client.models.generate_videos(
        model="veo-3.1-generate-preview",
        prompt="A simple test video of a red ball bouncing.",
    )
    print(f"✅ 비디오 모델 요청 접수 성공 (상태: {op.name})")
except errors.APIError as e:
    print(f"❌ 비디오 모델 요청 실패 (API Error): {e}")
except Exception as e:
    print(f"❌ 비디오 모델 요청 실패 (Other Error): {e}")
