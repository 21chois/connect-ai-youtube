import os
import sys
import time
import json
import random
from datetime import datetime
from dotenv import load_dotenv

# [설정] 프로젝트 루트 및 도구 폴더 경로 확보
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, ".agent", "tools"))

from image_shorts_maker import create_image_shorts
from youtube_auto_uploader import get_authenticated_service, upload_video, save_upload_record

def generate_smart_lotto_numbers():
    """스마트 로또 번호 추출기"""
    while True:
        nums = sorted(random.sample(range(1, 46), 6))
        total_sum = sum(nums)
        if 120 <= total_sum <= 180:
            return nums

def generate_jeju_lotto_video(account_id="sub"):
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🐾 조감독 영식: [제주 서귀포 올레시장 편] 링도사 로또 제작 시작")
    
    load_dotenv(os.path.join(BASE_DIR, ".env"))
    
    output_dir = "output_assets"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"lotto_jeju_olle_{timestamp}.mp4")
    
    # 로또 번호 생성
    num = generate_smart_lotto_numbers()
    print(f"🎯 링도사가 제주에서 점지한 번호: {num}")
    
    # 제주 서귀포 올레시장 컨셉 프롬프트
    base_prompts = [
        "Hyper-realistic 9:16 vertical shot of a majestic white cat (Ring-dosa) wearing a small traditional Korean hat, sitting on a wooden crate in the vibrant Seogwipo Olle Market, Jeju Island. In the background, busy market stalls with colorful fruits and fresh seafood. Cinematic lighting, morning sun.",
        "Hyper-realistic 9:16 vertical close-up of the mystical Ring-dosa looking kindly at a middle-aged Korean woman who is hard at work selling Hallabong oranges. The woman looks tired but has a kind smile. Soft golden aura around the cat.",
        "Hyper-realistic 9:16 vertical shot of Ring-dosa raising its paw toward the woman. Magical golden dust and blue energy (Do-ryeok) flow from the paw toward her hands. Background market crowd is blurred with bokeh.",
        "Hyper-realistic 9:16 vertical macro shot of glowing golden 3D lottery numbers appearing in the air between Ring-dosa and the woman. The numbers reflect in her eyes. High detail, magical atmosphere.",
        "Hyper-realistic 9:16 vertical shot of the woman holding a lottery ticket, looking shocked and grateful. Ring-dosa is sitting gracefully next to her, looking proud. Cinematic color grading, Jeju market atmosphere.",
        "Hyper-realistic 9:16 vertical shot of Ring-dosa waving its paw gently as it disappears into a soft mist in the middle of the market. A glowing 'SUBSCRIBE' sign in the air. 8k resolution, photorealistic."
    ]
    
    subtitles = [
        "여기는 활기찬 제주 서귀포 올레시장입니다.",
        "오늘 링도사의 눈에 들어온 한 분... 시장에서 누구보다 성실하게 일하시는 어머님입니다.",
        "착하고 성실한 그 마음, 링도사가 모를 리 없습니다. 오늘 특별히 나의 '도력'을 나누어 드리겠습니다.",
        "자, 어머님의 손끝으로 전해지는 이 우주의 기운... 보이십니까?",
        f"첫 번째 숫자는 {num[0]}, {num[1]}, {num[2]}번입니다. 꽉 잡으십시오.",
        "나머지 번호는 오직 성실한 자에게만 허락됩니다. 구독하고 '설명란'에서 확인하십시오."
    ]
    
    print("🎥 제주 스페셜 영상 생성 중...")
    try:
        from google import genai
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        success = create_image_shorts(
            client=client,
            prompt=base_prompts,
            output_path=output_path,
            subtitles=subtitles
        )
        if not success:
            raise Exception("영상 제작 실패")
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return False
            
    # SEO 및 업로드
    youtube_title = f"🔮 [제주 스페셜] 서귀포 올레시장에서 만난 링도사! 성실한 어머님께 점지한 로또 번호는?"
    seo_metadata = {
        "titles": [youtube_title],
        "description": f"📍 장소: 제주 서귀포 올레시장\n\n열심히 땀 흘리며 일하시는 우리 시장 어머님들을 위해\n링도사가 특별히 도력을 발휘했습니다! 🐾\n\n영상 속 번호: {num[0]}, {num[1]}, {num[2]}\n나머지 대박 번호: {num[3]}, {num[4]}, {num[5]}\n\n행운은 성실한 사람에게 찾아옵니다! 구독하고 기운 받아가세요!\n\n#로또 #제주도 #서귀포올레시장 #링도사 #로또번호 #운세 #시장풍경 #감동 #쇼츠",
        "tags": ["로또", "제주도", "서귀포", "올레시장", "링도사", "로또예상번호", "감동", "쇼츠"],
        "category_id": "22"
    }
    
    print("📤 유튜브 업로드 중...")
    youtube_service = get_authenticated_service(account_id=account_id)
    result = upload_video(youtube_service, output_path, seo_metadata, privacy_status="public")
    
    if result:
        save_upload_record(result["id"], result.get("title", ""), base_prompts[0], {}, output_path)
        print(f"✅ 제주 스페셜 미션 완료! {result.get('url')}")
        return True
    return False

if __name__ == "__main__":
    # 카이막 스페셜도 함께 가동하는 구조로 호출
    generate_jeju_lotto_video(account_id="sub")
