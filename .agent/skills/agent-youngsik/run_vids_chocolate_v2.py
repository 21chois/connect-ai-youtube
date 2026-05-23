import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# [설정] 프로젝트 루트 확보
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agent", "tools"))

load_dotenv(os.path.join(ROOT_DIR, ".env"))

from image_shorts_maker import create_image_shorts

def run_experiment():
    print("🧪 [Connect AI] Vids-Style Chocolate Experiment V2 가동")
    
    # 기획 데이터 (기존보다 훨씬 상세한 시네마틱 프롬프트)
    prompt = [
        "Cinematic extreme macro shot of a knife slowly slicing through a thick premium dark chocolate bar. Sharp cracks, dramatic side lighting, dark moody atmosphere, 8K.",
        "Extreme close-up of golden toasted knafeh noodles sizzling in melting butter in a rustic pan. Warm golden glow, cinematic smoke.",
        "Macro shot of vibrant neon-green pistachio cream being mixed with crispy golden noodles. Mesmerizing contrast, professional food photography lighting.",
        "Cinematic 9:16 vertical shot of a person taking a bite of the chocolate, face showing pure bliss. Blurred high-end cafe background, soft bokeh."
    ]
    
    subtitles = [
        "요즘 난리난 이 소리, 들리시나요? 두바이 초콜릿의 핵심, 바로 '카다이프'의 바삭함입니다.",
        "중동의 전통 국수 카다이프를 버터에 볶아 극강의 바삭함을 만들어내죠. 이게 바로 식감의 비밀입니다.",
        "여기에 진한 피스타치오 크림을 듬뿍 섞어주면, 우리가 아는 그 마법의 단면이 완성됩니다.",
        "단순한 유행이 아닙니다. 식감과 풍미의 완벽한 조화, 직접 경험해보세요."
    ]
    
    output_path = os.path.join(ROOT_DIR, "output_assets", f"vids_chocolate_exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
    
    try:
        from google import genai
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        print("\n🎨 [Vids Engine] 고화질 영상 제작 중... (약 3분 소요)")
        success = create_image_shorts(client, prompt, output_path, subtitles)
        
        if success:
            print(f"\n✅ 실험 성공! 결과물이 생성되었습니다.")
            print(f"📂 경로: {output_path}")
            print("💡 이 영상은 자동 업로드되지 않았습니다. 감독님께서 직접 로컬에서 확인해 주세요.")
        else:
            print("❌ 영상 생성 실패")
            
    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    run_experiment()
