from google import genai
import os
from dotenv import load_dotenv

# [설정] 프로젝트 루트 확보
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

def final_attempt():
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    op_file = "veo_op_id.txt"
    with open(op_file, "r") as f:
        op_name = f.read().strip()

    print(f"🔄 내부 API를 통한 작업({op_name}) 조회를 시도합니다...")
    
    try:
        # SDK 내부의 _api_client를 직접 사용하여 REST 호출 시도
        # google-genai는 pydantic/requests 기반이므로 내부 구조를 활용
        res = client.operations._get(op_name)
        print(f"✅ _get 성공! 상태: {'완료' if res.done else '진행 중'}")
        return res
    except Exception as e:
        print(f"❌ _get 실패: {e}")

    try:
        # vertexai 속성 확인
        if hasattr(client.operations, 'vertexai'):
            print("👉 Vertex AI 경로 시도...")
            res = client.operations.vertexai.get_operation(op_name)
            print(f"✅ Vertex 성공! 상태: {res}")
            return res
    except Exception as e:
        print(f"❌ Vertex 실패: {e}")

if __name__ == "__main__":
    final_attempt()
