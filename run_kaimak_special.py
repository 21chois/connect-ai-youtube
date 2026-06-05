import os
import sys
import json
from datetime import datetime

from dotenv import load_dotenv

# [수정] 파일 위치에 상관없이 프로젝트 루트와 도구 폴더를 정확히 찾도록 개선
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, ".agent", "tools"))

load_dotenv(os.path.join(BASE_DIR, ".env"))

from image_shorts_maker import create_image_shorts
from youtube_auto_uploader import get_authenticated_service, upload_video, save_upload_record, post_and_pin_comment

CONFIG_FILE = os.path.join(BASE_DIR, "kaimak_series_config.json")

def main():
    print("╔══════════════════════════════════════════════════════╗")
    print("║   🎬 Agent Young-sik | Kaimak Special Edition        ║")
    print("║   - 직함: 총괄 디렉터 (Director of Operations)       ║")
    print("║   - 모드: 긴급 트렌드 대응 (Trend Response)          ║")
    print("╚══════════════════════════════════════════════════════╝")
    
    if not os.path.exists(CONFIG_FILE):
        print("❌ 설정 파일이 없습니다.")
        return

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config_data = json.load(f)
    
    ep_data = config_data["episodes"][0] # EP.1 실행
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🧠 디렉터 영식: 카이막 스페셜 제작 시작")
    
    output_dir = os.path.join(BASE_DIR, "output_assets")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"kaimak_special_{timestamp}.mp4")
    
    print("🎥 [제작 봇] 영상 렌더링 중 (약 3~5분 소요)...")
    
    try:
        from google import genai
        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        success = create_image_shorts(
            client=client,
            prompt=ep_data["imagen_prompt"],
            output_path=output_path,
            subtitles=ep_data["subtitles"]
        )
        if not success:
            raise Exception("이미지 합성 에러")
    except Exception as e:
        print(f"❌ 제작 중 에러 발생: {e}")
        return

    print(f"✅ [제작 완료]: {output_path}")
    
    seo_metadata = {
        "titles": [ep_data["youtube_title"]],
        "description": (
            f"🥛 천상의 맛, 터키 전통 카이막 리얼 리뷰!\n\n"
            f"#{' #'.join(ep_data['youtube_tags'])}\n\n"
            f"🎁 [함께 즐기면 좋은 디저트 추천]\n"
            f"🍫 네이버 브랜드스토어 (수제 프리미엄):\n"
            f"👉 https://brand.naver.com/kimboramchocolate/products/3583065645\n\n"
            f"🚀 쿠팡 (로켓배송 BIG SIZE):\n"
            f"👉 https://www.coupang.com/vp/products/8367034324?itemId=24175542907&vendorItemId=91193524734\n\n"
            f"*(※ 파트너스 활동을 통해 일정액의 수수료를 제공받을 수 있습니다.)*\n"
        ),
        "tags": ep_data["youtube_tags"],
        "category_id": "22"
    }
    
    trend_info = {
        "product": "터키 프리미엄 카이막",
        "score": 98.0,
        "trend_reason": "데이터 분석가 Stats의 긴급 추천 아이템"
    }
    
    print("📤 [행정 봇] 유튜브 업로드 중... (타겟: 서브 계정)")
    youtube_service = get_authenticated_service(account_id="sub")
    result = upload_video(
        youtube_service=youtube_service,
        file_path=output_path,
        seo_metadata=seo_metadata,
        trend_info=trend_info,
        privacy_status="public",
        dry_run=False
    )
    
    if result:
        video_id = result["id"]
        save_upload_record(
            video_id=video_id,
            title=result.get("title", ""),
            veo_prompt=ep_data["imagen_prompt"][0],
            trend_info=trend_info,
            file_path=output_path
        )
        
        # [수익화] 고정 댓글 자동 작성
        comment_text = (
            f"🥛 카이막이랑 같이 먹으면 기절하는 '두바이 초콜릿' 좌표! 👇\n\n"
            f"🛒 네이버 브랜드스토어 (수제 프리미엄):\n"
            f"https://brand.naver.com/kimboramchocolate/products/3583065645\n\n"
            f"🚀 쿠팡 (로켓배송 BIG SIZE):\n"
            f"https://www.coupang.com/vp/products/8367034324?itemId=24175542907&vendorItemId=91193524734\n\n"
            f"이거 진짜 구하기 힘들어요! 있을 때 쟁여두세요! 🔥"
        )
        post_and_pin_comment(youtube_service, video_id, comment_text)
        
        print(f"\n🏆 [미션 완료] 카이막 영상 업로드 성공!")
        print(f"🔗 링크: {result.get('url')}")

if __name__ == "__main__":
    main()
