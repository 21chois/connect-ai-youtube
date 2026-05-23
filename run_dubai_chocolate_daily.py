import os
import sys
import time
import json
import schedule
from datetime import datetime
from dotenv import load_dotenv

# [설정] 프로젝트 루트 및 도구 폴더 경로 확보
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, ".agent", "tools"))

# 환경 변수 로드
load_dotenv(os.path.join(BASE_DIR, ".env"))

# 개별 미션 임포트
from youtube_auto_uploader import get_authenticated_service, upload_video, save_upload_record, post_and_pin_comment
from run_lotto_cat import generate_and_upload_lotto_cat as run_lotto

# 카이막 스페셜 임포트 (파일이 있을 경우에만)
try:
    from run_kaimak_special import main as run_kaimak
except ImportError:
    run_kaimak = None

# 상태 및 설정 파일 경로
STATE_FILE = os.path.join(BASE_DIR, ".agent", "memory", "series_state.json")
CONFIG_FILE = os.path.join(BASE_DIR, "dubai_series_config.json")

def get_current_episode():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
            return state.get("current_ep", 1)
    return 1

def update_episode(ep_num):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"current_ep": ep_num}, f)

def generate_and_upload_chocolate(time_slot="테스트", account_id="main"):
    ep_num = get_current_episode()
    
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ 설정 파일이 없습니다: {CONFIG_FILE}")
        return False
        
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config_data = json.load(f)
    
    episodes = config_data.get("episodes", [])
    if not episodes:
        print("❌ 시리즈 설정 데이터가 없습니다.")
        return False
        
    ep_data = next((ep for ep in episodes if ep["ep_number"] == ep_num), None)
    if not ep_data:
        print(f"⚠️ EP.{ep_num} 데이터 부족 -> 1화 루프 리셋")
        ep_num = 1
        ep_data = episodes[0]
        
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🎬 [Mission: Chocolate] EP.{ep_num} 시작")
    
    output_dir = os.path.join(BASE_DIR, "output_assets")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"dubai_series_ep{ep_num}_{timestamp}.mp4")
    
    # [감독님 지시] VidS 대신 이미지 쇼츠 모드 우선 가동
    try:
        from image_shorts_maker import create_image_shorts
        from google import genai
        print(f"   🎨 이미지 쇼츠 생성 모드 가동 (Prompt: {len(ep_data['imagen_prompt'])} 컷)")
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        success = create_image_shorts(client, ep_data["imagen_prompt"], output_path, ep_data["subtitles"])
        if not success: raise Exception("이미지 쇼츠 생성 실패")
    except Exception as e:
        print(f"❌ 생성 에러: {e}")
        return False
            
    # SEO & Upload
    seo_metadata = {
        "titles": [ep_data["youtube_title"]],
        "description": (
            f"📦 두바이 초콜릿 유니버스 시리즈 EP.{ep_num}\n\n"
            f"🍫 [구매 좌표 1] 네이버 브랜드스토어 (수제 프리미엄):\n"
            f"👉 https://brand.naver.com/kimboramchocolate/products/3583065645\n\n"
            f"🚀 [구매 좌표 2] 쿠팡 (로켓배송 BIG SIZE):\n"
            f"👉 https://www.coupang.com/vp/products/8367034324?itemId=24175542907&vendorItemId=91193524734\n\n"
            f"#{' #'.join(ep_data['youtube_tags'])}\n"
            f"*(※ 파트너스 활동을 통해 일정액의 수수료를 제공받을 수 있습니다.)*\n"
        ),
        "tags": ep_data["youtube_tags"],
        "category_id": "22"
    }
    
    youtube_service = get_authenticated_service(account_id=account_id)
    result = upload_video(youtube_service, output_path, seo_metadata, privacy_status="public")
    
    if result:
        video_id = result["id"]
        save_upload_record(video_id, result.get("title", ""), ep_data["imagen_prompt"], {}, output_path)
        
        # [수익화] 고정 댓글 자동 작성
        comment_text = (
            f"🍫 영상 속 그 초콜릿! 여기서 바로 확인하세요! 👇\n\n"
            f"🛒 네이버 브랜드스토어 (프리미엄 수제):\n"
            f"https://brand.naver.com/kimboramchocolate/products/3583065645\n\n"
            f"🚀 쿠팡 (로켓배송 BIG SIZE):\n"
            f"https://www.coupang.com/vp/products/8367034324?itemId=24175542907&vendorItemId=91193524734\n\n"
            f"※ 품절 전 득템하세요! 🔥"
        )
        post_and_pin_comment(youtube_service, video_id, comment_text)
        
        update_episode(ep_num + 1 if ep_num < len(episodes) else 1)
        print(f"✅ 초콜릿 미션 완료: {result.get('url')}")
        return True
    return False

def job_wrapper(func, name, *args, **kwargs):
    print(f"\n{'='*60}")
    print(f"🚀 [Connect AI] {name} 미션 시작 ({datetime.now().strftime('%H:%M:%S')})")
    print(f"{'='*60}")
    try:
        if func:
            func(*args, **kwargs)
            print(f"✅ [Connect AI] {name} 미션 성공")
        else:
            print(f"⚠️ [Connect AI] {name} 실행 함수가 없습니다.")
    except Exception as e:
        print(f"❌ [Connect AI] {name} 에러: {e}")

def main():
    print("╔══════════════════════════════════════════════════════╗")
    print("║   🏢 Connect AI | Mega Orchestrator (V2.0-Upgraded)  ║")
    print("║   - 조감독 영식 (Agent Young-sik) 통합 관리 모드      ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 즉시 1회 테스트 실행 (원치 않으시면 아래 줄을 주석 처리하세요)
    job_wrapper(generate_and_upload_chocolate, "초기 테스트", time_slot="최초 실행", account_id="main")
    
    print("\n⏳ 초기 실행 완료. 이제 정해진 스케줄(12:00, 19:00)을 대기합니다.")
    
    # 2. 스케줄링 루프
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # [12:00] 메인: 두바이 초콜릿 / 서브: 카이막 스페셜
        if current_time == "12:00":
            print(f"\n⏰ 정오(12:00) 미션 개시!")
            # 메인 채널: 두바이 초콜릿
            job_wrapper(generate_and_upload_chocolate, "메인: 두바이 초콜릿", account_id="main")
            
            # 서브 채널: 카이막 스페셜
            if run_kaimak:
                job_wrapper(run_kaimak, "서브: 카이막 스페셜", account_id="sub")
            
            time.sleep(60) # 중복 실행 방지
            
        # [18:00] 서브: 링도사 로또 (제주 스페셜)
        elif current_time == "18:00":
            print(f"\n⏰ 오후 6시(18:00) 링도사 미션 개시!")
            from run_lotto_jeju_olle import generate_jeju_lotto_video
            job_wrapper(generate_jeju_lotto_video, "서브: 링도사 제주 로또", account_id="sub")
            
            time.sleep(60) # 중복 실행 방지
            
        time.sleep(30)

if __name__ == "__main__":
    main()
