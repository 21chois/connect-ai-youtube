import os
import sys
from datetime import datetime

# [설정] 프로젝트 루트 및 도구 폴더 경로 확보
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agent", "tools"))

from youtube_auto_uploader import get_authenticated_service, upload_video, save_upload_record

def upload_chocolate_video():
    print(f"🚀 [Agent Young-sik] 두바이 초콜릿 쇼츠 업로드 시작 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    
    # 1. 파일 확인
    target_file = os.path.join(ROOT_DIR, "output_assets", "dubai_final_shorts.mp4")
    if not os.path.exists(target_file):
        print(f"❌ 업로드할 파일을 찾을 수 없습니다: dubai_final_shorts.mp4")
        return

    # [중요] 작업 디렉토리를 루트로 변경하여 인증 파일들을 찾을 수 있게 함
    os.chdir(ROOT_DIR)

    # 2. 서비스 인증
    print("🔑 유튜브 API 인증 중...")
    youtube_service = get_authenticated_service(account_id="sub")
    if not youtube_service:
        print("❌ 인증 실패")
        return

    # 3. SEO 메타데이터 설정 (A안)
    seo_metadata = {
        "titles": ["🤯 이 소리 실화? 두바이 초콜릿 '극강의 바삭함' 비밀 폭로 l #쇼츠 #두바이초콜릿"],
        "description": (
            "두바이 초콜릿의 핵심은 초콜릿이 아니라 바로 '소리'입니다.\n"
            "중동 전통의 카다이프 면을 버터에 볶아 피스타치오 크림과 섞었을 때의 그 쾌감!\n\n"
            "조감독 영식이 데이터로 분석한 가장 맛있는 단면을 시각화했습니다.\n"
            "🛒 구매 좌표: [댓글창 고정 링크 확인]\n\n"
            "#두바이초콜릿 #카다이프 #피스타치오 #ASMR #쇼츠리뷰 #AI영상"
        ),
        "tags": ["두바이초콜릿", "카다이프", "피스타치오", "ASMR", "쇼츠리뷰", "AI영상", "디저트맛집"],
        "category_id": "22"
    }

    # 4. 업로드 수행
    print(f"📤 파일 업로드 중: {os.path.basename(target_file)}")
    try:
        result = upload_video(
            youtube_service=youtube_service,
            file_path=target_file,
            seo_metadata=seo_metadata,
            trend_info={"product": "두바이 초콜릿", "score": 98.5},
            privacy_status="private" # 안전하게 비공개로 먼저 업로드
        )
        
        if result:
            print(f"\n✅ 업로드 대성공!")
            print(f"🔗 URL: {result.get('url')}")
            print(f"📌 상태: 비공개 (유튜브 스튜디오에서 공개 전환 가능)")
            
            # 히스토리 기록
            save_upload_record(
                video_id=result["id"],
                title=seo_metadata["titles"][0],
                veo_prompt="Vids Internal Rendering Style",
                trend_info={"product": "두바이 초콜릿"},
                file_path=target_file
            )
        else:
            print("❌ 업로드 실패 (결과값 없음)")
    except Exception as e:
        print(f"❌ 업로드 과정 중 에러 발생: {e}")

if __name__ == "__main__":
    upload_chocolate_video()
