import os
import sys
import time
import json
from datetime import datetime
from dotenv import load_dotenv

# [설정] 프로젝트 루트 및 도구 폴더 경로 확보
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, ".agent", "tools"))

# 환경 변수 로드
load_dotenv(os.path.join(BASE_DIR, ".env"))

from youtube_auto_uploader import get_authenticated_service, upload_video, save_upload_record, post_and_pin_comment
from image_shorts_maker import create_image_shorts
from google import genai

CONFIG_FILE = os.path.join(BASE_DIR, "k_defense_config.json")

def generate_and_upload_k_defense(ep_id="k_def_01"):
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ 설정 파일이 없습니다: {CONFIG_FILE}")
        return False
        
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config_data = json.load(f)
    
    items = config_data.get("items", [])
    ep_data = next((item for item in items if item["id"] == ep_id), None)
    
    if not ep_data:
        print(f"❌ '{ep_id}' 데이터를 찾을 수 없습니다.")
        return False
        
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 [Mission: K-Defense] {ep_data['name']} 생성 시작")
    
    output_dir = os.path.join(BASE_DIR, "output_assets")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"{ep_id}_{timestamp}.mp4")
    
    try:
        print(f"   🎨 이미지 쇼츠 생성 모드 가동 (Prompt: {len(ep_data['imagen_prompt'])} 컷)")
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        success = create_image_shorts(client, ep_data["imagen_prompt"], output_path, ep_data["subtitles"])
        if not success: 
            raise Exception("이미지 쇼츠 생성 실패")
    except Exception as e:
        print(f"❌ 생성 에러: {e}")
        return False
            
    # SEO & Upload
    seo_metadata = {
        "titles": [ep_data["youtube_title"]],
        "description": (
            f"🚀 {ep_data['youtube_title']}\n\n"
            f"압도적인 국방력, 대한민국 K-방산의 자부심을 함께 느껴보세요.\n"
            f"더 많은 밀리터리/방산 소식이 궁금하시다면 구독과 좋아요 부탁드립니다!\n\n"
            f"#{' #'.join(ep_data['youtube_tags'])}\n"
        ),
        "tags": ep_data["youtube_tags"],
        "category_id": "22"  # People & Blogs or Entertainment
    }
    
    print(f"   📺 유튜브 업로드 준비 중...")
    youtube_service = get_authenticated_service(account_id="main")
    result = upload_video(youtube_service, output_path, seo_metadata, privacy_status="public")
    
    if result:
        video_id = result["id"]
        save_upload_record(video_id, result.get("title", ""), ep_data["imagen_prompt"], {}, output_path)
        
        # 고정 댓글 작성 (커머스 링크 대신 구독 유도 및 국뽕 메시지)
        comment_text = (
            f"🇰🇷 우리 기술로 만든 자랑스러운 K-방산!\n"
            f"가슴 웅장해지는 대한민국 국방력에 응원의 한 마디를 댓글로 남겨주세요! 👇\n\n"
            f"구독과 좋아요는 큰 힘이 됩니다! 🫡"
        )
        post_and_pin_comment(youtube_service, video_id, comment_text)
        
        print(f"✅ K-방산({ep_data['name']}) 업로드 완료: {result.get('url')}")
        return True
    return False

if __name__ == "__main__":
    generate_and_upload_k_defense("k_def_01")
