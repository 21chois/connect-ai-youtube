import os
import sys
import json
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 툴 경로 추가
sys.path.insert(0, os.path.abspath(".agent/tools"))
from veo_video_maker import generate_long_take

load_dotenv()

def run_chocolate_veo_test():
    print("[Veo 3.1] Dubai Chocolate High-Quality Video Generation Started")
    print("?   - 직함: 조감독 (Assistant Director)                ?")
    print("?   - 모드: 시리즈 루프 (Series Loop)                  ?")
    print("?   - 업로드 스케줄: 매일 12:00, 19:00                ?")
    
    output_dir = "output_assets"
    os.makedirs(output_dir, exist_ok=True)
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # 1. 에피소드 데이터 로드 (EP.1 기준)
    with open("dubai_series_config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    ep_data = config["episodes"][0]
    
    # 2. 시드 이미지 생성
    print("\nPhase 1: Generating Seed Image (Dubai Chocolate)...")
    seed_img_path = os.path.join(output_dir, "chocolate_seed.jpg")
    
    # Veo 3.1을 위한 고퀄리티 시드 프롬프트 재구성
    image_prompt = (
        "Cinematic 9:16 vertical extreme macro shot of a thick, premium Dubai chocolate bar being broken in half. "
        "Intense focus on the interior filling: bright green pistachio cream mixed with crispy golden toasted knafeh strings. "
        "Gooey texture, molten chocolate drips, luxury marble background, soft volumetric lighting, 8k resolution, professional food photography."
    )
    
    try:
        img_result = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=image_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="9:16"
            )
        )
        for generated_image in img_result.generated_images:
            img = Image.open(BytesIO(generated_image.image.image_bytes))
            img.save(seed_img_path, "JPEG", quality=95)
            print(f"Seed image saved: {seed_img_path}")
    except Exception as e:
        print(f"Seed image generation failed: {e}")
        return

    # 3. Veo 3.1 롱테이크 영상 생성
    print("\nPhase 2: Rendering Veo 3.1 Long-take Video...")
    
    base_video_prompt = (
        "The camera slowly zooms in on the bright green pistachio filling. "
        "The chocolate drips realistically and the crispy knafeh strings glisten under the light. "
        "Slow, cinematic motion."
    )
    
    extend_prompts = [
        "A hand enters the frame and picks up a piece of the chocolate. The filling stretches slightly as it's lifted."
    ]
    
    output_filename = os.path.join(output_dir, "chocolate_veo_test.mp4")
    
    try:
        generate_long_take(
            image_path=seed_img_path,
            base_prompt=base_video_prompt,
            extend_prompts=extend_prompts,
            output_filename=output_filename
        )
        print(f"\n[Success] High-quality Veo Chocolate video saved: {output_filename}")
    except Exception as e:
        print(f"Veo video generation failed: {e}")

if __name__ == "__main__":
    run_chocolate_veo_test()
