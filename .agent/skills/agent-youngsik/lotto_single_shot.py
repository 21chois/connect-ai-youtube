import os
import sys
import json
from datetime import datetime

# 프로젝트 루트 경로 확보
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SKILL_DIR, "..", "..", ".."))

# 경로 추가 및 임포트
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, ".agent", "tools"))

try:
    from youtube_auto_uploader import get_authenticated_service, upload_video, save_upload_record
    
    print("🚀 [링도사 스페셜] 제주 올레시장 편 업로드 전용 모드 가동...")
    
    # 가장 최근에 생성된 제주 영상 찾기
    output_dir = os.path.join(ROOT_DIR, "output_assets")
    target_video = None
    import glob
    video_files = glob.glob(os.path.join(output_dir, "lotto_jeju_olle_*.mp4"))
    if video_files:
        target_video = max(video_files, key=os.path.getmtime)
    
    if not target_video:
        print("❌ 업로드할 영상 파일을 찾을 수 없습니다.")
        sys.exit(1)
        
    print(f"✅ 대상 영상 확인: {os.path.basename(target_video)}")
    
    # SEO 및 트렌드 정보 설정
    num = [9, 10, 16, 17, 42, 45] # 방금 생성된 번호 고정
    trend_info = {
        "product": "링도사 제주 로또",
        "score": 100.0,
        "trend_reason": "제주 서귀포 올레시장 스페셜"
    }
    
    youtube_title = f"🔮 [제주 스페셜] 서귀포 올레시장에서 만난 링도사! 성실한 어머님께 점지한 로또 번호는?"
    seo_metadata = {
        "titles": [youtube_title],
        "description": f"📍 장소: 제주 서귀포 올레시장\n\n링도사가 특별히 도력을 발휘했습니다! 🐾\n\n전체 번호: {num[0]}, {num[1]}, {num[2]}, {num[3]}, {num[4]}, {num[5]}\n\n#로또 #제주도 #서귀포올레시장 #링도사 #로또번호 #감동 #쇼츠",
        "tags": ["로또", "제주도", "서귀포", "올레시장", "링도사", "로또예상번호", "감동", "쇼츠"],
        "category_id": "22"
    }
    
    # 업로드 실행 (경로 문제 해결을 위해 CWD를 ROOT_DIR로 임시 변경)
    os.chdir(ROOT_DIR)
    youtube_service = get_authenticated_service(account_id='sub')
    result = upload_video(
        youtube_service=youtube_service,
        file_path=target_video,
        seo_metadata=seo_metadata,
        trend_info=trend_info,
        privacy_status="private"
    )
    
    if result:
        save_upload_record(result["id"], result.get("title", ""), "Jeju Special", trend_info, target_video)
        print(f"\n🏆 [미션 완료] 제주 링도사 업로드 성공! 링크: {result.get('url')}")

except Exception as e:
    print(f"❌ 실행 중 오류 발생: {e}")
