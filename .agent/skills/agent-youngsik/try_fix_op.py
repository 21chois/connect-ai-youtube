from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

# [설정] 프로젝트 루트 확보
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

def try_fix():
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # 기존 작업 ID 읽기
    op_file = "veo_op_id.txt"
    if not os.path.exists(op_file):
        print("❌ 작업 ID 파일이 없습니다.")
        return
        
    with open(op_file, "r") as f:
        op_name = f.read().strip()

    print(f"🔄 작업 ID({op_name})로 상태 조회를 시도합니다...")
    
    try:
        # 방법 5: 최소 기능 객체(Proxy) 사용
        print("👉 시도 5: 단순 Proxy 객체(name 속성 포함) 사용")
        class ProxyOp:
            def __init__(self, name):
                self.name = name
        
        dummy_op = ProxyOp(op_name)
        operation = client.operations.get(dummy_op)
        print(f"✅ 성공! 상태: {'완료' if operation.done else '진행 중'}")
        return operation
    except Exception as e:
        print(f"❌ 시도 5 실패: {e}")

    try:
        # 방법 2: 키워드 인자 'operation' 사용
        print("\n👉 시도 2: 키워드 인자 operation= 사용")
        operation = client.operations.get(operation=op_name)
        print(f"✅ 성공! 상태: {'완료' if operation.done else '진행 중'}")
        return operation
    except Exception as e:
        print(f"❌ 시도 2 실패: {e}")

    try:
        # 방법 3: 단순 문자열 전달 (이미 실패했었지만 다시 확인)
        print("\n👉 시도 3: 단순 문자열 전달")
        operation = client.operations.get(op_name)
        print(f"✅ 성공! 상태: {'완료' if operation.done else '진행 중'}")
        return operation
    except Exception as e:
        print(f"❌ 시도 3 실패: {e}")

if __name__ == "__main__":
    try_fix()
