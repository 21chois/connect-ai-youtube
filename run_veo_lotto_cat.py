import os
import sys
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 툴 경로 추가
sys.path.insert(0, os.path.abspath(".agent/tools"))
from veo_video_maker import generate_long_take
from youtube_auto_uploader import get_authenticated_service, upload_video, save_upload_record

load_dotenv()

def run_lotto_cat_veo():
    print("[Veo 3.1] Lotto Cat High-Quality Video Generation Started")
    
    output_dir = "output_assets"
    os.makedirs(output_dir, exist_ok=True)
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # 1. 시드 이미지(Imagen 4.0) 생성 - Veo의 첫 프레임으로 사용
    seed_img_path = os.path.join(output_dir, "lotto_cat_seed.jpg")
    
    if os.path.exists(seed_img_path):
        print(f"✅ Existing seed image found: {seed_img_path}. Skipping generation.")
    else:
        print("\nPhase 1: Generating Seed Image...")
        image_prompt = (
            "Hyper-realistic 9:16 vertical portrait of a majestic, mystical white cat dressed as a traditional Korean shaman. "
            "The cat is wearing intricate, highly detailed colorful silk robes and a black Gat (Korean hat). "
            "The cat sits in a dark, foggy mystical temple at night. Dramatic volumetric lighting, 8k resolution, cinematic masterpiece."
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

    # 2. Veo 3.1 롱테이크 영상 생성
    print("\nPhase 2: Rendering Veo 3.1 Long-take Video...")
    
    base_video_prompt = (
        "The majestic shaman cat slowly opens its glowing golden eyes and stares intensely into the camera. "
        "The cat's fur and the surrounding mystical fog move realistically in slow motion."
    )
    
    extend_prompts = [
        "A close-up of the cat's paw as it slowly touches a floating, glowing golden lottery ball. Magical sparks emanate from the contact point."
    ]
    
    output_filename = os.path.join(output_dir, "lotto_cat_veo_serious.mp4")
    
    try:
        generate_long_take(
            image_path=seed_img_path,
            base_prompt=base_video_prompt,
            extend_prompts=extend_prompts,
            output_filename=output_filename
        )
        print(f"\n[Success] High-quality Veo video saved: {output_filename}")

        # --- YouTube 업로드 추가 ---
        print(f"\n📤 유튜브 업로드 중... (타겟 계정: sub)")
        try:
            seo_metadata = {
                "titles": ["🔮 [초고화질] 냥도사의 신비로운 로또 운세 (Veo 3.1 AI)"],
                "description": "Veo 3.1로 생성된 초고화질 냥도사 영상입니다.\n\n#로또 #냥도사 #AI영상 #Veo3 #고양이 #행운",
                "tags": ["로또", "고양이", "운세", "행운", "AI영상", "Veo3.1"],
                "category_id": "22"
            }
            trend_info = {
                "product": "냥도사 로또 Veo High-Q",
                "score": 99.0
            }

            youtube_service = get_authenticated_service(account_id="sub")
            result = upload_video(
                youtube_service=youtube_service,
                file_path=output_filename,
                seo_metadata=seo_metadata,
                trend_info=trend_info,
                privacy_status="private"
            )

            if result and not result.get("dry_run"):
                save_upload_record(
                    video_id=result["id"],
                    title=result.get("title", ""),
                    veo_prompt=base_video_prompt,
                    trend_info=trend_info,
                    file_path=output_filename
                )
                print(f"✅ 업로드 완료! 유튜브 링크: {result.get('url')}")
        except Exception as upload_err:
            print(f"❌ 업로드 중 에러 발생: {upload_err}")

    except Exception as e:
        print(f"Veo video generation failed: {e}")

if __name__ == "__main__":
    run_lotto_cat_veo()
