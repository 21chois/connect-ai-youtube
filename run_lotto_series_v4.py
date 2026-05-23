import os
import sys
import time
import json
import random
from datetime import datetime
from dotenv import load_dotenv

# Add tools to path
sys.path.insert(0, os.path.abspath(".agent/tools"))

try:
    from image_shorts_maker import create_image_shorts
    from youtube_auto_uploader import get_authenticated_service, upload_video, save_upload_record
except ImportError as e:
    print(f"Error importing tools: {e}")
    sys.exit(1)

load_dotenv()

STATE_FILE = ".agent/memory/lotto_series_state.json"
CONFIG_FILE = "lotto_series_config.json"

def get_current_episode():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
                return state.get("current_ep", 1)
        except:
            return 1
    return 1

def update_episode(ep_num):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"current_ep": ep_num, "last_run": datetime.now().isoformat()}, f)

def generate_lucky_numbers():
    return sorted(random.sample(range(1, 46), 6))

def run_ringdosa_production(account_id="sub"):
    ep_num = get_current_episode()
    
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ 설정 파일({CONFIG_FILE})이 없습니다.")
        return False
        
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config_data = json.load(f)
    
    episodes = config_data.get("episodes", [])
    ep_data = next((ep for ep in episodes if ep["ep_number"] == ep_num), None)
    
    if not ep_data:
        print(f"⚠️ EP.{ep_num} 데이터가 없습니다. 1화로 루프를 다시 시작합니다.")
        ep_num = 1
        ep_data = next((ep for ep in episodes if ep["ep_number"] == ep_num), episodes[0])
        
    print("\n" + "✨" * 30)
    print(f"  [Agent Young-sik] Ringdosa Universe Production: EP.{ep_num}")
    print(f"  Theme: {ep_data['theme']}")
    print("  Status: Seeking for High-End Cinematic Quality")
    print("✨" * 30 + "\n")
    
    output_dir = "output_assets"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"ringdosa_v4_ep{ep_num}_{timestamp}.mp4")
    
    # 럭키 넘버 생성 및 자막에 주입 (EP.3, 4, 5 등에서 활용)
    lucky_nums = generate_lucky_numbers()
    num_str = ", ".join([str(n) for n in lucky_nums])
    
    final_subtitles = []
    for s in ep_data["subtitles"]:
        final_subtitles.append(s.replace("{num_str}", num_str))
        
    print(f"🔮 오늘의 행운 번호: {num_str}")
    
    # 영상 생성 (Premium Mode)
    from google import genai
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    print("🎥 영상 제작 중 (Premium Cinematic Mode)...")
    success = create_image_shorts(
        client=client,
        prompt=ep_data["imagen_prompt"],
        output_path=output_path,
        subtitles=final_subtitles
    )
    
    if not success:
        print("❌ 영상 생성 실패")
        return False
        
    # 유튜브 업로드
    seo_metadata = {
        "titles": [ep_data["youtube_title"]],
        "description": f"✨ 링도사 유니버스 EP.{ep_num}: {ep_data['theme']}\n\n{final_subtitles[0]}\n\n🔮 오늘의 행운 번호: {num_str}\n\n#{' #'.join(ep_data['youtube_tags'])}\n\n#로또 #링도사 #자동화 #AI조감독",
        "tags": ep_data["youtube_tags"],
        "category_id": "22"
    }
    
    print(f"📤 유튜브 업로드 중... (타겟: {account_id})")
    try:
        youtube_service = get_authenticated_service(account_id=account_id)
        result = upload_video(
            youtube_service=youtube_service,
            file_path=output_path,
            seo_metadata=seo_metadata,
            trend_info={"product": f"Ringdosa V4 EP.{ep_num}", "score": 100.0},
            privacy_status="public" # 바로 공개
        )
        
        if result:
            save_upload_record(
                video_id=result["id"],
                title=result.get("title", ""),
                veo_prompt=ep_data["imagen_prompt"][0],
                trend_info={"product": f"Ringdosa V4 EP.{ep_num}", "score": 100.0},
                file_path=output_path
            )
            print(f"✅ 업로드 완료! 주소: {result.get('url')}")
            
            # 다음 회차 업데이트
            next_ep = ep_num + 1
            if next_ep > len(episodes):
                next_ep = 1 # 루프
            update_episode(next_ep)
            return True
    except Exception as e:
        print(f"❌ 업로드 중 오류 발생: {e}")
        return False

def main():
    # 즉시 1회 실행 테스트
    run_ringdosa_production()

if __name__ == "__main__":
    main()
