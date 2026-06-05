import os
import json
import time
import sys
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

# [수정] 파일 위치에 상관없이 프로젝트 루트와 도구 폴더를 정확히 찾도록 개선
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, ".agent", "tools"))

load_dotenv(os.path.join(BASE_DIR, ".env"))

from image_shorts_maker import create_image_shorts
from veo_video_maker import generate_long_take
from youtube_auto_uploader import get_authenticated_service, upload_video, save_upload_record

load_dotenv()

def find_trending_item(client):
    """Gemini Search를 사용하여 현재 한국에서 가장 핫한 커머스 아이템 발굴"""
    print("Searching for trending commerce items...")
    
    prompt = """
    2026년 5월 현재, 한국의 유튜브, 틱톡, 인스타그램에서 가장 바이럴되고 있는 
    '편의점 신상'이나 '식품/라이프스타일 템' 1가지를 선정해주세요.
    선정한 아이템의 이름, 바이럴 이유(식감, 맛, 희귀성 등), 그리고 이를 주제로 한 숏폼 대본(4문장)을 작성해주세요.
    
    출력 형식 (JSON):
    {
        "item_name": "아이템 이름",
        "reason": "바이럴 이유 요약",
        "scene1": "후킹 문구 (예: 요즘 이거 없어서 못 산다면서요?)",
        "scene2": "제품 특징 및 비주얼 묘사",
        "scene3": "직접 먹어보거나 써본 듯한 생생한 반응",
        "scene4": "어디서 살 수 있는지와 마무리",
        "visual_prompt": "이 제품을 표현할 고화질 시네마틱 이미지 프롬프트 (영어)"
    }
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearchRetrieval())],
            response_mime_type="application/json",
        ),
        contents=prompt
    )
    return json.loads(response.text)

def main():
    print("="*60)
    print("[Agent Young-sik] Viral Commerce Trend V1")
    print("="*60)

    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    # 1. 트렌드 아이템 발굴
    trend = find_trending_item(client)
    print(f"Target Item: {trend['item_name']}")

    # 2. 스토리보드 구성
    STORYBOARD = [
        {"prompt": f"Cinematic close-up of {trend['item_name']}, {trend['visual_prompt']}, 8K, high detail, commercial lighting.", "subtitle": trend["scene1"]},
        {"prompt": f"Close-up of {trend['item_name']} being used or opened, highly detailed textures, vibrant colors.", "subtitle": trend["scene2"]},
        {"prompt": f"Emotional reaction shot of a person enjoying {trend['item_name']} (anime or realistic style), warm lighting.", "subtitle": trend["scene3"]},
        {"prompt": f"The product {trend['item_name']} placed on a wooden table with soft sunlight, aesthetic composition.", "subtitle": trend["scene4"]}
    ]

    prompts = [item["prompt"] for item in STORYBOARD]
    subtitles = [item["subtitle"] for item in STORYBOARD]

    output_dir = os.path.join(BASE_DIR, "output_assets")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = os.path.join(output_dir, f"commerce_trend_{timestamp}.mp4")

    # 3. 영상 생성 (Stable Mode as default for speed/reliability in commerce)
    print("\nStarting video generation...")
    success = create_image_shorts(client, prompts, output_filename, subtitles)

    if success:
        # 4. 유튜브 업로드
        print("\nUploading to YouTube... (Target: sub)")
        try:
            seo_metadata = {
                "titles": [f"🔥 {trend['item_name']}! 요즘 이거 모르면 아싸? #shorts"],
                "description": f"{trend['reason']}\n\n{trend['scene1']}\n\n{trend['scene2']}\n\n#품절대란 #편의점신상 #트렌드 #리뷰 #내돈내산",
                "tags": [trend['item_name'], "트렌드", "리뷰", "편의점", "핫템"],
                "category_id": "22"
            }
            trend_info = {"product": trend['item_name'], "score": 95.0}

            youtube_service = get_authenticated_service(account_id="sub")
            result = upload_video(
                youtube_service=youtube_service,
                file_path=output_filename,
                seo_metadata=seo_metadata,
                trend_info=trend_info,
                privacy_status="public"
            )
            print(f"DONE! YouTube Link: {result.get('url')}")
        except Exception as upload_err:
            print(f"[Error] Upload failed: {upload_err}")

if __name__ == "__main__":
    main()
