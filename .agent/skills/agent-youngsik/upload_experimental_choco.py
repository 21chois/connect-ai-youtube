import os
import sys
import json
from datetime import datetime

# [설정] 프로젝트 루트 확보
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SKILL_DIR, "..", "..", ".."))

# 작업 디렉토리를 루트로 변경 (인증 파일 및 에셋 경로 정합성 확보)
os.chdir(ROOT_DIR)

# .agent/tools 경로를 sys.path에 추가 (ROOT_DIR 기준)
sys.path.insert(0, os.path.join(ROOT_DIR, ".agent", "tools"))

# 환경 변수 로드를 위해 루트 .env 로드
from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT_DIR, ".env"))

try:
    from youtube_auto_uploader import get_authenticated_service, upload_video, save_upload_record
except ImportError:
    print("❌ youtube_auto_uploader.py를 찾을 수 없습니다. 경로 설정을 확인하세요.")
    sys.exit(1)

def upload_experimental():
    print("🚀 [실험] 고화질 두바이 초콜릿 실험 영상 업로드 시작")
    
    # 대상 파일 (ROOT 기준)
    target_file = "output_assets/vids_chocolate_exp_20260513_215656.mp4"
    full_path = os.path.join(ROOT_DIR, target_file)
    
    if not os.path.exists(full_path):
        print(f"❌ 파일을 찾을 수 없습니다: {full_path}")
        return

    # 인증 (메인 채널 - 'main' 계정 사용)
    print("🔑 유튜브 API 인증 시도 중...")
    youtube_service = get_authenticated_service(account_id="main")
    if not youtube_service:
        print("❌ 유튜브 인증 실패. 브라우저 인증이 필요할 수 있습니다.")
        return

    # SEO 최적화 메타데이터
    seo_metadata = {
        "titles": ["✨ [Premium] 화제의 두바이 초콜릿, Veo 3.1로 구현한 역대급 고화질 시네마틱 l #품절대란 #쇼츠"],
        "description": "두바이 초콜릿의 끝판왕 비주얼을 감상하세요.\nAI 조감독 영식이 Veo 3.1 엔진을 풀 가동하여 제작한 실험적 시네마틱 영상입니다.\n\n#두바이초콜릿 #실화 #고화질 #Veo #AI영상 #쇼츠 #디저트 #품절대란",
        "tags": ["두바이초콜릿", "실화", "고화질", "Veo", "AI영상", "쇼츠", "디저트", "품절대란", "먹방", "리뷰"],
        "category_id": "22"
    }

    print(f"📦 업로드 준비 완료: {target_file}")
    
    try:
        # 업로드 실행 (즉시 공개: public)
        result = upload_video(
            youtube_service=youtube_service,
            file_path=full_path,
            seo_metadata=seo_metadata,
            trend_info={"product": "dubai_chocolate_experimental", "score": 98.0},
            privacy_status="public" 
        )
        
        if result:
            # 업로드 기록 저장 (중요: memory 폴더에 기록하여 중복 업로드 방지 및 추적)
            save_upload_record(
                video_id=result["id"],
                title=result.get("title", ""),
                veo_prompt="Veo 3.1 Experimental: Dubai Chocolate",
                trend_info={"product": "dubai_chocolate_experimental"},
                file_path=full_path
            )
            print(f"\n✅ [최종 보고] 업로드 성공: {result.get('url')}")
            print("대표님, 실험 영상 송출이 완료되었습니다. 알고리즘 유입을 모니터링하겠습니다.")
    except Exception as e:
        print(f"❌ 업로드 실패: {e}")

if __name__ == "__main__":
    upload_experimental()
