import os
import random
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types
import sys

# Add tools directory to path
sys.path.append(os.path.join(os.getcwd(), ".agent", "tools"))
from image_shorts_maker import create_image_shorts
from veo_video_maker import generate_long_take
from youtube_auto_uploader import get_authenticated_service, upload_video, save_upload_record

load_dotenv()

def generate_lucky_numbers():
    return sorted(random.sample(range(1, 46), 6))

def generate_story(client, nums):
    """Gemini를 사용하여 오늘의 힐링 스토리와 번호에 담긴 의미를 생성"""
    num_str = ", ".join([f"{n}번" for n in nums])
    
    prompt = f"""
    당신은 '냥도사'라는 이름의 신비로운 무당 고양이입니다. 
    오늘의 행운 번호는 {num_str}입니다.
    
    이 번호들과 관련된 짧고 신비로운 힐링 스토리를 4문장으로 작성해주세요.
    말투는 고양이 컨셉(~다냥, ~라냥)이어야 하며, 시청자에게 위로와 희망을 주는 따뜻한 톤이어야 합니다.
    
    출력 형식 (JSON):
    {{
        "scene1": "첫인사와 오늘의 분위기 (힐링 메시지)",
        "scene2": "번호를 뽑게 된 신비로운 상황 설명",
        "scene3": "번호 {num_str}를 공개하며 행운을 빌어주는 말",
        "scene4": "마지막 인사와 구독 당부"
    }}
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
        contents=prompt
    )
    return json.loads(response.text)

def main():
    print("="*60)
    print("[Agent Young-sik] Lotto Cat V3: Cinematic Storytelling")
    print("="*60)

    # API 클라이언트 초기화
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # 1. 행운 번호 및 스토리 생성
    nums = generate_lucky_numbers()
    story = generate_story(client, nums)
    num_str = ", ".join([f"{n}번" for n in nums])
    
    print(f"Generated Story: {story['scene1'][:30]}...")

    # 2. 스토리보드 구성
    STORYBOARD = [
        {
            "prompt": "Cinematic 9:16 shot of a mystical shaman cat meditating in a peaceful ancient temple, soft glowing incense smoke, morning sunlight, ultra-HD, photorealistic.",
            "subtitle": story["scene1"]
        },
        {
            "prompt": "The shaman cat gently ringing a golden bell, magical gold dust floating in the air, mystical atmosphere, warm studio lighting.",
            "subtitle": story["scene2"]
        },
        {
            "prompt": "A beautiful spread of 6 lucky numbers floating over a silk cushion, elegant presentation, mystical energy, soft bokeh background.",
            "subtitle": story["scene3"]
        },
        {
            "prompt": "The shaman cat softly waving its paw towards the camera, healing and warm atmosphere, daily promise message.",
            "subtitle": story["scene4"]
        }
    ]

    prompts = [item["prompt"] for item in STORYBOARD]
    subtitles = [item["subtitle"] for item in STORYBOARD]

    output_dir = "output_assets"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = os.path.join(output_dir, f"lotto_cat_v3_{timestamp}.mp4")

    # 3. 영상 생성 실행 (Veo 3.1 attempt with Fallback)
    print("\nStarting video generation flow...")
    success = False
    
    # Veo 3.1 시도
    print("[Step 1] Veo 3.1 High-Quality Attempt...")
    try:
        from PIL import Image
        from io import BytesIO
        
        seed_img_path = os.path.join(output_dir, f"lotto_seed_{timestamp}.jpg")
        img_result = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=prompts[0],
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="9:16"
            )
        )
        for generated_image in img_result.generated_images:
            img = Image.open(BytesIO(generated_image.image.image_bytes))
            img.save(seed_img_path, "JPEG", quality=95)
            
        generate_long_take(
            image_path=seed_img_path,
            base_prompt=prompts[1],
            extend_prompts=prompts[2:],
            output_filename=output_filename
        )
        success = True
        print("[Success] Veo 3.1 generation complete!")
    except Exception as e:
        print(f"[Warning] Veo 3.1 failed: {e}")
        print("[Step 2] Switching to Stable Mode...")
        success = create_image_shorts(client, prompts, output_filename, subtitles)

    if success:
        # 4. 유튜브 업로드
        print("\nUploading to YouTube... (Target: sub)")
        try:
            seo_metadata = {
                "titles": [f"🔮 냥도사의 {datetime.now().strftime('%m월 %d일')} 행운 예언"],
                "description": f"{story['scene1']}\n\n{story['scene2']}\n\n오늘의 번호: {num_str}\n\n#로또 #냥도사 #힐링 #운세 #고양이 #행운",
                "tags": ["로또", "고양이", "운세", "행운", "복권", "냥도사", "힐링"],
                "category_id": "22"
            }
            trend_info = {"product": "냥도사 로또 V3", "score": 100.0}

            youtube_service = get_authenticated_service(account_id="sub")
            result = upload_video(
                youtube_service=youtube_service,
                file_path=output_filename,
                seo_metadata=seo_metadata,
                trend_info=trend_info,
                privacy_status="public"
            )

            if result and not result.get("dry_run"):
                save_upload_record(
                    video_id=result["id"],
                    title=result.get("title", ""),
                    veo_prompt=prompts[0],
                    trend_info=trend_info,
                    file_path=output_filename
                )
                print(f"DONE! YouTube Link: {result.get('url')}")
        except Exception as upload_err:
            print(f"[Error] Upload failed: {upload_err}")
    else:
        print("[Error] Video generation failed.")

if __name__ == "__main__":
    main()
