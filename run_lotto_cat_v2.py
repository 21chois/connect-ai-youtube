import os
import random
import json
from datetime import datetime
from dotenv import load_dotenv
from google import genai
import sys
sys.path.append(os.path.join(os.getcwd(), ".agent", "tools"))
from image_shorts_maker import create_image_shorts
from veo_video_maker import generate_long_take
from youtube_auto_uploader import get_authenticated_service, upload_video, save_upload_record

load_dotenv()

# 1. 냥도사 V4 스토리 보드 (6개 번호 통합 노출 버전)
STORYBOARD = [
    {
        "prompt": "Cinematic 9:16 shot of a mystical shaman cat meditating in a peaceful ancient temple, soft glowing incense smoke, morning sunlight, ultra-HD, photorealistic.",
        "subtitle": "오늘 하루도 참 고생 많았다냥. 잠시 쉬어가라냥."
    },
    {
        "prompt": "The shaman cat gently ringing a golden bell, magical gold dust floating in the air, mystical atmosphere, warm studio lighting.",
        "subtitle": "그대의 맑은 기운을 모아 오늘의 번호를 뽑았다냥!"
    },
    {
        "prompt": "A beautiful spread of 6 lucky numbers floating over a silk cushion, elegant presentation, mystical energy, soft bokeh background.",
        "subtitle": "★ 전체 행운 번호: "
    },
    {
        "prompt": "Close-up of the shaman cat smiling wisely, warm lighting, 8K quality, soft focus background.",
        "subtitle": "이 6개 숫자가 그대에게 큰 기쁨이 되길 빌겠다냥!"
    },
    {
        "prompt": "The shaman cat softly waving its paw towards the camera, healing and warm atmosphere, daily promise message.",
        "subtitle": "매일 이 시간, 냥도사와 행운의 약속! 내일 또 만나자냥."
    }
]

def generate_lucky_numbers():
    """1~45 사이의 중복 없는 랜덤 번호 6개 생성"""
    return sorted(random.sample(range(1, 46), 6))

def main():
    print("="*60)
    print("[Agent Young-sik] Lotto Cat V2: Healing & Luck")
    print("="*60)

    # API 클라이언트 초기화
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # 랜덤 번호 생성
    nums = generate_lucky_numbers()
    num_str = ", ".join([f"{n}번" for n in nums]) # 1번, 2번.. 형식으로 더 자연스럽게 읽히도록 수정
    print(f"Generated Lucky Numbers: {num_str}")

    # 번호 삽입 (3번째 자막에 전체 6개 번호 정보 추가)
    # 기존 자막 뒤에 번호를 붙여서 누락되지 않도록 함
    STORYBOARD[2]["subtitle"] = f"전체 행운 번호는 {num_str}입니다."

    prompts = [item["prompt"] for item in STORYBOARD]
    subtitles = [item["subtitle"] for item in STORYBOARD]

    output_dir = "output_assets"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = os.path.join(output_dir, f"lotto_cat_v2_{timestamp}.mp4")

    # 영상 생성 실행
    print("\nStarting video generation flow...")
    
    # --- Veo 3.1 고화질 모드 시도 ---
    success = False
    print("\n[Step 1] Veo 3.1 High-Quality Generation Attempt...")
    try:
        # 1. 시드 이미지 생성 (Veo의 첫 프레임용)
        from PIL import Image
        from io import BytesIO
        from google.genai import types
        
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
            
        # 2. Veo 롱테이크 생성 시도
        generate_long_take(
            image_path=seed_img_path,
            base_prompt=prompts[1],
            extend_prompts=prompts[2:],
            output_filename=output_filename
        )
        success = True
        print("[Success] Veo 3.1 generation successful!")
    except Exception as e:
        print(f"[Warning] Veo 3.1 failed (Quota issue, etc): {e}")
        print("[Step 2] Switching to Stable Mode (Imagen + MoviePy)...")
        
        # --- Fallback: 일반 모드 실행 ---
        success = create_image_shorts(client, prompts, output_filename, subtitles)

    if success:
        print(f"\n[Success] Lotto Cat V2 video created: {output_filename}")
        
        # 메타데이터 준비 (YouTube 업로드용)
        metadata = {
            "title": f"🍀 [매일행운] 냥도사의 로또 예상 번호 배달 (매일 업데이트!)",
            "description": f"지친 당신을 위한 냥도사의 힐링 행운 배달 서비스!\n\n매일 이 시간, 당신의 행운을 책임지고 배달해드리기로 약속합니다.\n\n오늘의 예상 번호: {num_str}\n\n#로또 #냥도사 #매일행운 #고양이 #행운 #운세 #로또번호",
            "tags": ["로또", "고양이", "운세", "행운", "복권", "냥도사", "매일행운", "예상번호"],
            "video_path": output_filename
        }
        
        with open(f"logs/metadata_lotto_{timestamp}.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        # --- YouTube upload attempt ---
        print(f"\nUploading to YouTube... (Target: sub)")
        try:
            # SEO 메타데이터 형식 맞춤 (upload_video 함수 요구사항)
            seo_metadata = {
                "titles": [metadata["title"]],
                "description": metadata["description"],
                "tags": metadata["tags"],
                "category_id": "22"
            }
            trend_info = {
                "product": "냥도사 로또 V2",
                "score": 99.0
            }

            youtube_service = get_authenticated_service(account_id="sub")
            result = upload_video(
                youtube_service=youtube_service,
                file_path=output_filename,
                seo_metadata=seo_metadata,
                trend_info=trend_info,
                privacy_status="public" # 자동 스케줄링이므로 공개로 업로드
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
        print("\n[Error] Video generation failed.")

if __name__ == "__main__":
    main()
