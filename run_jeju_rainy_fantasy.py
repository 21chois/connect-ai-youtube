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

def main():
    print("╔══════════════════════════════════════════════════════╗")
    print("║   🎬 Agent Young-sik | Jeju Fantasy Production       ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🌙 조감독 영식: 제작 개시")
    
    # 1. 의존성 체크
    print("\n[Step 1] 의존성 라이브러리 체크 중...")
    dependencies = ["google.genai", "moviepy", "PIL", "dotenv", "edge_tts"]
    missing = []
    for dep in dependencies:
        try:
            if dep == "edge_tts":
                import subprocess
                subprocess.run(["edge-tts", "--version"], capture_output=True, check=True)
            else:
                __import__(dep.replace(".", ""))
            print(f" ✅ {dep} 로드 성공")
        except Exception:
            print(f" ❌ {dep} 로드 실패")
            missing.append(dep)
    
    if missing:
        print(f"\n⚠️ 다음 라이브러리가 부족합니다: {', '.join(missing)}")
        print("💡 해결책: pip install google-genai moviepy Pillow python-dotenv edge-tts")
        return

    # 2. 환경 변수 체크
    load_dotenv(os.path.join(BASE_DIR, ".env"))
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.startswith("YOUR_"):
        print("❌ 에러: GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return
    print(" ✅ 환경 변수 로드 완료")
    
    output_dir = os.path.join(BASE_DIR, "output_assets")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"jeju_rainy_fantasy_{timestamp}.mp4")
    
    # 로또 번호 생성
    num = generate_smart_lotto_numbers()
    num_str = ", ".join(map(str, num))
    print(f"🎯 링선비가 빗속에서 점지한 번호: {num_str}")
    
    # 프롬프트 및 자막 설정
    base_prompts = [
        "A hyper-realistic 9:16 vertical cinematic still of a traditional Jeju market alley just after a heavy rainfall. The wet, dark basalt stone floor intensely reflects the colorful neon and warm yellow lights from traditional shop signboards. Puddles of water on the uneven ground create a mirror-like surface. A soft, blue-toned misty atmosphere hangs in the air. Moody, emotional, 8k resolution, cinematic lighting.",
        "A mysterious white cat wearing a traditional Korean black 'Gat' (hat) and a flowing white 'Dopo' (scholar's robe), standing silently in a dark, shadowy corner of a rainy Jeju market. The cat's eyes glow with a subtle golden wisdom. Its silhouette is sharp against the hazy background of the market. Korean fantasy aesthetic, subtle mystery, high detail fur texture, photorealistic.",
        "A close-up of a middle-aged Korean merchant in the Jeju market, working tirelessly at a small seafood or orange stall. The merchant’s face shows deep exhaustion but an expression of honest integrity and kindness. Raindrops still cling to the stall's plastic roof. In the blurry background, the cat scholar's silhouette is faintly visible, watching over them. Emotional storytelling, high-detail skin texture, cinematic color grading.",
        "A wide-angle cinematic shot where the cat scholar in white robes stands among a crowd of blurred, moving shoppers. The cat figure is standing perfectly still, seemingly ethereal and glowing with a faint, soft light, yet blending naturally into the market environment. The contrast between the mundane reality of the market and the legendary presence of the cat.",
        "A macro shot of the cat scholar's paw gently raised toward the wet basalt floor. Where the paw points, the reflection of the light in the puddle transforms into glowing, ancient Korean characters and golden lottery numbers. The ripples in the water create a magical, shimmering effect."
    ]
    
    subtitles = [
        "비가 갓 그친 제주의 재래시장, 차가운 공기가 코끝을 스칩니다.",
        "젖은 현무암 바닥에 어린 화려한 불빛들... 그 그림자 속에 누군가 있습니다.",
        "고단한 하루를 정직하게 채워가는 이의 뒷모습.",
        "전설 속 '링선비'가 그 묵묵한 성실함에 작은 기적을 선물하려 합니다.",
        f"선비가 남긴 번호는 {num[0]}, {num[1]}, {num[2]}... 행운은 늘 당신 곁에 있습니다."
    ]
    
    print("\n[Step 2] 영상 엔진 가동 중 (3~5분 소요)...")
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        success = create_image_shorts(
            client=client,
            prompt=base_prompts,
            output_path=output_path,
            subtitles=subtitles
        )
        if not success:
            raise Exception("이미지 합성 에러 (로그를 확인해주세요)")
    except Exception as e:
        print(f"\n❌ [ERROR] 제작 실패: {e}")
        import traceback
        traceback.print_exc()
        return

    print(f" ✅ [제작 완료]: {output_path}")
    
    # 업로드
    print("\n[Step 3] 유튜브 업로드 중...")
    try:
        youtube_title = f"🔮 [제주 판타지] 비 내린 올레시장에 나타난 '링선비'의 축복... 당신의 번호는?"
        seo_metadata = {
            "titles": [youtube_title],
            "description": f"📍 장소: 비 갠 뒤의 제주 재래시장\n\n#로또 #제주도 #올레시장 #링도사 #링선비 #판타지 #감동쇼츠 #로또번호",
            "tags": ["로또", "제주도", "올레시장", "링선비"],
            "category_id": "22"
        }
        
        youtube_service = get_authenticated_service(account_id="sub")
        result = upload_video(youtube_service, output_path, seo_metadata, privacy_status="private")
        
        if result:
            save_upload_record(result["id"], result.get("title", ""), base_prompts[0], {}, output_path)
            print(f"\n🏆 [성공] 업로드 완료! 링크: {result.get('url')}")
    except Exception as e:
        print(f" ⚠️ 업로드 실패 (영상은 로컬에 저장됨): {e}")

if __name__ == "__main__":
    main()
