import os
import sys
from datetime import datetime

# [설정] 프로젝트 루트 및 도구 폴더 경로 확보
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# skill 폴더인 경우 parent의 parent가 root
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agent", "tools"))

from youtube_auto_uploader import get_authenticated_service, upload_video

def real_test_upload():
    print(f"🚀 [REAL TEST] 유튜브 업로드 테스트 시작 ({datetime.now()})")
    
    # 1. 파일 확인
    target_file = os.path.join(ROOT_DIR, "output_assets", "kaimak_special_20260511_213221.mp4")
    if not os.path.exists(target_file):
        print(f"❌ 파일을 찾을 수 없습니다: {target_file}")
        return

    # [중요] 작업 디렉토리를 루트로 변경하여 client_secret.json을 찾을 수 있게 함
    os.chdir(ROOT_DIR)

    # 2. 서비스 인증 및 채널 확인
    print("🔑 인증 및 채널 확인 중...")
    youtube_service = get_authenticated_service(account_id="sub")
    if not youtube_service:
        print("❌ 인증 실패")
        return
        
    try:
        channels = youtube_service.channels().list(part="snippet", mine=True).execute()
        channel_title = channels["items"][0]["snippet"]["title"]
        print(f"📺 대상 채널: [{channel_title}]")
    except Exception as e:
        print(f"❌ 채널 정보 획득 실패: {e}")
        return

    # 3. 업로드 수행 (PUBLIC 설정)
    print("📤 실제 업로드 중 (PUBLIC)...")
    seo_metadata = {
        "titles": [f"[영식 테스트] 천상의 맛 카이막 - {datetime.now().strftime('%m%d %H:%M')}"],
        "description": "조감독 영식의 시스템 복구 및 업로드 기능 테스트 영상입니다.",
        "tags": ["테스트", "영식", "카이막"],
        "category_id": "22"
    }
    
    try:
        result = upload_video(
            youtube_service=youtube_service,
            file_path=target_file,
            seo_metadata=seo_metadata,
            trend_info={"product": "test_kaimak"},
            privacy_status="public"
        )
        
        if result:
            print(f"\n✅ 업로드 대성공!")
            print(f"🔗 URL: {result.get('url')}")
            print(f"📌 채널: {channel_title}")
        else:
            print("❌ 업로드 결과가 없습니다.")
    except Exception as e:
        print(f"❌ 업로드 과정 중 에러 발생: {e}")

if __name__ == "__main__":
    real_test_upload()
