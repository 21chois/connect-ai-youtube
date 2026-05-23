import inspect
from google import genai
import os
from dotenv import load_dotenv

# [설정] 프로젝트 루트 확보
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

def check_params():
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    try:
        sig = inspect.signature(client.operations.get)
        print(f"Signature of client.operations.get: {sig}")
    except Exception as e:
        print(f"Could not get signature: {e}")

if __name__ == "__main__":
    check_params()
