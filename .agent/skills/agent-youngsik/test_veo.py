import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# [설정] 프로젝트 루트 확보
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

def test_veo_generation():
    print("🚀 [Veo 3.1] 차세대 비디오 생성 엔진 테스트 시작...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ API Key가 없습니다.")
        return

    client = genai.Client(api_key=api_key)
    
    # 초콜릿 실험용 테스트 프롬프트
    prompt = "Cinematic extreme macro shot of dark chocolate melting, golden caramel flowing inside, 8K, highly detailed, vertical 9:16."
    
    print(f"🎬 생성 요청 중: '{prompt}'")
    try:
        # Veo 3.1 프리뷰 모델 시도
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio="9:16",
                resolution="720p", # 테스트용으로 낮은 해상도 시도
            ),
        )
        
        print("⏳ 비디오 생성 중... (Operation ID: {})".format(operation.id if hasattr(operation, 'id') else 'Pending'))
        
        # 3번만 폴링해보고 상태 확인
        for _ in range(3):
            if operation.done:
                break
            print("... 대기 중 ...")
            time.sleep(10)
            operation = client.operations.get(operation)
            
        if operation.done:
            print("✅ 비디오 생성 성공!")
            # 실제 다운로드는 시간이 걸리므로 성공 여부만 확인
        else:
            print("⏳ 생성 중입니다. (시간 관계상 비동기로 계속 진행됨)")
            
    except Exception as e:
        print(f"❌ Veo 엔진 접근 실패: {e}")
        print("💡 팁: 해당 API 키에 Veo 3.1 프리뷰 권한이 있는지 확인이 필요합니다.")

if __name__ == "__main__":
    test_veo_generation()
