import os
import sys
import time
import json
import random
from datetime import datetime

# [수정] 파일 위치에 상관없이 프로젝트 루트와 도구 폴더를 정확히 찾도록 개선
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, ".agent", "tools"))

from image_shorts_maker import create_image_shorts
from youtube_auto_uploader import get_authenticated_service, upload_video, save_upload_record

def generate_smart_lotto_numbers():
    """역대 1등 당첨 통계를 반영한 스마트 로또 번호 추출기"""
    while True:
        nums = sorted(random.sample(range(1, 46), 6))
        
        # 1. 총합 필터 (120 ~ 180)
        total_sum = sum(nums)
        if not (120 <= total_sum <= 180):
            continue
            
        # 2. 홀짝 비율 필터 (3:3, 4:2, 2:4)
        odds = sum(1 for n in nums if n % 2 != 0)
        evens = 6 - odds
        if (odds, evens) not in [(3, 3), (4, 2), (2, 4)]:
            continue
            
        # 3. 고저 비율 필터 (1~22 vs 23~45)
        lows = sum(1 for n in nums if n <= 22)
        highs = 6 - lows
        if (lows, highs) not in [(3, 3), (4, 2), (2, 4)]:
            continue
            
        # 4. 연속 번호 필터 (3개 이상 연속 금지)
        consecutive_count = 1
        max_consecutive = 1
        for i in range(5):
            if nums[i+1] - nums[i] == 1:
                consecutive_count += 1
                if consecutive_count > max_consecutive:
                    max_consecutive = consecutive_count
            else:
                consecutive_count = 1
        
        if max_consecutive >= 3:
            continue
            
        return nums

def generate_and_upload_lotto_cat(account_id="sub"):
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🐾 조감독 영식: 냥도사 로또 추첨 쇼츠 생성 시작")
    
    output_dir = "output_assets"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"lotto_cat_{timestamp}.mp4")
    thumb_path = os.path.join(output_dir, f"lotto_thumb_{timestamp}.jpg")
    
    # 빅데이터 스마트 로또 번호 추출
    lotto_numbers = generate_smart_lotto_numbers()
    num = lotto_numbers
    print(f"🎯 오늘 냥도사가 점지한 번호: {num}")
    
    base_prompts = [
        "Hyper-realistic 9:16 vertical portrait of a majestic, mystical white cat dressed as a traditional Korean shaman. The cat is wearing intricate, highly detailed colorful silk robes and a black Gat (Korean traditional hat). Ultra-detailed fur, dramatic volumetric lighting, foggy mystical temple background. Shot on 85mm lens, cinematic 8k.",
        "Hyper-realistic 9:16 vertical macro shot of the shaman cat's face illuminated by the bright blue glow of a crystal ball. Inside the crystal ball, realistic lottery balls with numbers are swirling. Extremely detailed cat eyes reflecting the light, cinematic depth of field.",
        "Hyper-realistic 9:16 vertical close-up of a realistic fluffy cat paw touching a glowing golden lottery ball. Magical golden sparks and realistic smoke are emitting from the contact point. Macro photography, sharp focus on the paw texture, dark mystical background.",
        "Hyper-realistic 9:16 vertical shot of the shaman cat standing on its hind legs, casting a spell. Glowing golden 3D lottery numbers are floating in the air realistically, casting golden light onto the highly detailed cat's fur. Masterpiece, unreal engine 5 render style realism.",
        "Hyper-realistic 9:16 vertical dynamic shot of the mystical cat performing a shamanic ritual, shaking a traditional brass bell. Golden dust is flying in slow motion. Motion blur, sharp focus on the cat's intense expression, rich cinematic colors.",
        "Hyper-realistic 9:16 vertical extreme close-up of the cat's face. The cat has piercing, hyper-realistic glowing golden eyes with highly detailed irises. A mysterious, almost human-like knowing smirk on its face. Perfect studio lighting, ultra-sharp fur.",
        "Hyper-realistic 9:16 vertical shot of the shaman cat guarding a luxurious, highly detailed traditional Korean silk fortune pouch (Bokjumeoni). The pouch is bursting with realistic gold coins and glowing lottery tickets. Beautiful bokeh background.",
        "Hyper-realistic 9:16 vertical shot of the majestic shaman cat sitting gracefully, waving its paw gently at the camera. In the background, a realistic glowing neon sign saying 'SUBSCRIBE' illuminates the dark mystical room. Cinematic lighting, photorealistic."
    ]
    
    subtitles = [
        "안녕하냥! 우주 최고 영험한 냥도사가 왔당~",
        "단순한 찍기가 아니다냥! 냥도사가 역대 1등 당첨 패턴을 빅데이터로 완벽하게 분석했다냥!",
        "자, 눈을 감고 우주의 기운을 모아서 뽑은 첫 번째, 두 번째 숫자는...",
        f"바로 {num[0]}번! 그리고 {num[1]}번이다냥! 기운이 팍팍 느껴지냥?",
        "이어서 재물운이 폭발하는 세 번째, 네 번째 숫자는...",
        f"무려 {num[2]}번과 {num[3]}번! 이건 까먹지 말고 무조건 적어둬라냥.",
        "가장 중요한 마지막 두 개의 숫자는 아무나 볼 수 없다냥!",
        "지금 당장 구독과 좋아요를 누르고, 영상 제목 밑에 있는 '더보기(설명란)'를 열어서 확인하라냥!"
    ]
    
    print("🎥 영상을 생성합니다 (약 3~5분 소요)...")
    try:
        from google import genai
        from google.genai import types
        client = genai.Client()
        
        print("🖼️ 맞춤형 16:9 썸네일 생성 중...")
        thumb_result = client.models.generate_images(
            model='imagen-3.0-generate-001',
            prompt="Cinematic 16:9 wide shot of a majestic mystical white cat dressed as a traditional Korean shaman. The cat is holding a glowing golden lottery ball with '1st' written on it. Huge glowing 'JACKPOT' neon sign in the background. Hyper-realistic, dramatic lighting, 8k resolution.",
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="16:9"
            )
        )
        for generated_image in thumb_result.generated_images:
            from PIL import Image
            from io import BytesIO
            img = Image.open(BytesIO(generated_image.image.image_bytes))
            img.save(thumb_path, "JPEG", quality=95)
            print(f"✅ 썸네일 저장 완료: {thumb_path}")
            
        success = create_image_shorts(
            client=client,
            prompt=base_prompts,
            output_path=output_path,
            subtitles=subtitles
        )
        if not success:
            raise Exception("이미지 합성 에러")
    except Exception as e:
        print(f"❌ 영상 생성 중 에러 발생: {e}")
        return False
            
    print(f"✅ 영상 생성 완료: {output_path}")
    
    trend_info = {
        "product": "냥도사 로또 추첨",
        "score": 99.0,
        "trend_reason": "무당 고양이 100% 자동화 파이프라인 (B채널)"
    }
    
    youtube_title = f"🔮 소름주의.. 영험한 냥도사가 알려주는 이번주 로또 1등 번호 ({num[0]}, {num[1]}...)"
    
    seo_metadata = {
        "titles": [youtube_title],
        "description": f"💰 냥도사의 기운을 받아가라냥!\n\n영상에서 공개하지 않은 마지막 '진짜' 행운의 두 숫자는...\n바로 [ {num[4]}번 ] 과 [ {num[5]}번 ] 이다냥!! 🐾\n\n전체 번호: {num[0]}, {num[1]}, {num[2]}, {num[3]}, {num[4]}, {num[5]}\n\n구독을 누른 사람에게만 이 번호의 재물운이 강력하게 발동한다냥! 1등 당첨 미리 축하한다냥!\n\n#로또 #로또예상번호 #로또1등 #운세 #사주 #고양이 #쇼츠 #냥도사 #재물운\n",
        "tags": ["로또", "로또번호", "로또예상번호", "운세", "사주", "타로", "고양이", "무당고양이", "쇼츠", "재물운", "행운"],
        "category_id": "22" # People & Blogs
    }
    
    print(f"📤 유튜브 업로드 중... (타겟 계정: {account_id})")
    youtube_service = get_authenticated_service(account_id=account_id)
    result = upload_video(
        youtube_service=youtube_service,
        file_path=output_path,
        seo_metadata=seo_metadata,
        trend_info=trend_info,
        privacy_status="private",
        dry_run=False,
        custom_thumbnail_path=thumb_path
    )
    
    if result and not result.get("dry_run"):
        save_upload_record(
            video_id=result["id"],
            title=result.get("title", ""),
            veo_prompt=base_prompts[0],
            trend_info=trend_info,
            file_path=output_path
        )
        print(f"✅ 냥도사 로또 영상 완료! 유튜브 링크: {result.get('url')}")
        return True
    return False

if __name__ == "__main__":
    generate_and_upload_lotto_cat(account_id="sub")
