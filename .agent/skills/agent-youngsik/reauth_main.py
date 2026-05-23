import os
import sys
import pickle

# [설정] 프로젝트 루트 확보
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agent", "tools"))

from youtube_auto_uploader import get_authenticated_service

def reauth():
    print("🚀 [Main 채널 권한 재갱신] 프로세스 시작")
    os.chdir(ROOT_DIR)
    
    token_path = "token_upload.pickle"
    if os.path.exists(token_path):
        print(f"🗑️ 기존 권한 파일 삭제 중: {token_path}")
        os.remove(token_path)
    
    print("\n🔑 새로운 브라우저 인증 창을 엽니다...")
    print("⚠️ 주의: 반드시 '메인 채널'로 사용할 구글 계정을 선택하고, 모든 권한(YouTube 업로드 및 조회)을 허용해 주세요.")
    
    try:
        service = get_authenticated_service(account_id="main")
        if service:
            channels = service.channels().list(part="snippet", mine=True).execute()
            title = channels["items"][0]["snippet"]["title"]
            print(f"\n✅ 인증 성공! 연결된 채널: [{title}]")
        else:
            print("❌ 인증 실패")
    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    reauth()
