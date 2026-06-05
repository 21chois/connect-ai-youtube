import os
import sys
from datetime import datetime

# Add tools to path
sys.path.insert(0, os.path.abspath(".agent/tools"))

from veo_video_maker import generate_long_take
from youtube_auto_uploader import get_authenticated_service, upload_video, save_upload_record

def main():
    print("🎬 사용자 특별 요청: 고양이가 요리하는 먹방 (20초)")
    output_dir = "output_assets"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"cat_mukbang_{timestamp}.mp4")
    
    # 기본 이미지 (흰색 이미지 생성)
    sample_img = os.path.join(output_dir, "sample_input.jpg")
    if not os.path.exists(sample_img):
        from PIL import Image
        img = Image.new("RGB", (1280, 720), color=(240, 240, 245))
        img.save(sample_img, "JPEG")
        
    # 커스텀 프롬프트 작성
    base_prompt = (
        "Cinematic 16:9 shot of an adorable fluffy ginger cat standing on its hind legs in a cozy, rustic kitchen. "
        "The cat is wearing a tiny chef's hat and apron, actively chopping vegetables on a wooden cutting board with a small knife. "
        "Warm natural sunlight streaming through a window. Ultra-HD, 8K, photo-realistic, highly detailed."
    )
    
    extend_prompts = [
        # 5~10초
        "The camera pans slightly. The cat is now stirring a simmering pot of stew with a wooden spoon. "
        "Steam is rising from the pot. The cat looks very focused and professional. Cinematic lighting, photorealistic.",
        # 10~15초
        "Close-up shot of the cat plating the food beautifully onto a ceramic dish. "
        "The cat carefully places a garnish of parsley on top. Soft bokeh background, 8K, highly detailed.",
        # 15~20초
        "The cat sits at the table and starts eating the delicious meal with absolute joy, doing a cute mukbang. "
        "The cat looks incredibly happy. Warm, inviting atmosphere, photorealistic, cinematic."
    ]
    
    print("🎥 영상을 생성합니다 (약 3~5분 소요)...")
    generate_long_take(
        image_path=sample_img,
        base_prompt=base_prompt,
        extend_prompts=extend_prompts,
        output_filename=output_path
    )
    
    print(f"✅ 영상 생성 완료: {output_path}")
    
    # 유튜브 업로드 설정
    trend_info = {
        "product": "고양이 요리 먹방",
        "score": 99.0,
        "trend_reason": "사용자 특별 요청"
    }
    seo_metadata = {
        "titles": [
            "🔥 심쿵주의! 직접 요리해서 먹방까지 하는 천재 고양이 셰프 🧑‍🍳🐾",
            "📺 (힐링) 고양이가 직접 끓인 스튜 먹방! 진짜 귀여움 주의"
        ],
        "description": "📦 너무 귀여운 고양이 셰프의 요리부터 먹방까지!\n\n🐾 힐링하고 가세요~\n#고양이 #먹방 #요리하는고양이 #동물먹방 #힐링",
        "tags": ["고양이", "먹방", "요리", "고양이요리", "힐링", "귀여운", "반려동물", "cat", "mukbang"],
        "category_id": "15" # Pets & Animals
    }
    
    print("📤 유튜브 업로드 중...")
    youtube_service = get_authenticated_service()
    result = upload_video(
        youtube_service=youtube_service,
        file_path=output_path,
        seo_metadata=seo_metadata,
        trend_info=trend_info,
        privacy_status="private",
        dry_run=False
    )
    
    if result and not result.get("dry_run"):
        save_upload_record(
            video_id=result["id"],
            title=result.get("title", ""),
            veo_prompt=base_prompt,
            trend_info=trend_info,
            file_path=output_path
        )
        print(f"✅ 완료! 유튜브 링크: {result.get('url')}")

if __name__ == "__main__":
    main()
