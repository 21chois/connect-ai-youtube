
import os
import sys
import json
from datetime import datetime

# [설정] 프로젝트 루트 및 도구 폴더 경로 확보
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, ".agent", "tools"))

from youtube_auto_uploader import get_authenticated_service, upload_video, save_upload_record

def force_upload():
    print("🚀 [긴급] 미업로드 영상 강제 업로드 프로세스 시작")
    
    # 대상 파일 정의
    targets = [
        {
            "file": "output_assets/lotto_jeju_olle_20260512_231958.mp4",
            "type": "lotto_jeju_olle",
            "title": "🔮 [제주 스페셜] 서귀포 올레시장에서 만난 링도사! 성실한 어머님께 점지한 로또 번호는? (최종본)",
            "tags": ["로또", "제주도", "서귀포", "올레시장", "링도사", "로또예상번호", "감동", "쇼츠"],
            "desc": "📍 장소: 제주 서귀포 올레시장\n\n열심히 땀 흘리며 일하시는 우리 시장 어머님들을 위해\n링도사가 특별히 도력을 발휘했습니다! 🐾\n\n행운은 성실한 사람에게 찾아옵니다! 구독하고 기운 받아가세요!\n\n#로또 #제주도 #서귀포올레시장 #링도사 #로또번호 #운세 #시장풍경 #감동 #쇼츠"
        }
    ]

    youtube_service = get_authenticated_service(account_id="sub")
    if not youtube_service:
        print("❌ 유튜브 서비스 인증 실패. 브라우저 확인이 필요할 수 있습니다.")
        return

    for t in targets:
        full_path = os.path.join(BASE_DIR, t["file"])
        if not os.path.exists(full_path):
            print(f"⚠️ 파일을 찾을 수 없음: {full_path}")
            continue

        print(f"\n📤 업로드 중: {t['file']}")
        seo_metadata = {
            "titles": [t["title"]],
            "description": t["desc"],
            "tags": t["tags"],
            "category_id": "22"
        }
        
        try:
            result = upload_video(
                youtube_service=youtube_service,
                file_path=full_path,
                seo_metadata=seo_metadata,
                trend_info={"product": t["type"]},
                privacy_status="private"
            )
            
            if result:
                save_upload_record(
                    video_id=result["id"],
                    title=result.get("title", ""),
                    veo_prompt=f"Force Upload: {t['type']}",
                    trend_info={"product": t["type"]},
                    file_path=full_path
                )
                print(f"✅ 업로드 성공: {result.get('url')}")
        except Exception as e:
            print(f"❌ {t['file']} 업로드 실패: {e}")

if __name__ == "__main__":
    force_upload()
