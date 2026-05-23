import os
import sys
import json
from datetime import datetime

def generate_chocolate_storyboard():
    print("🎬 [Vids-Style Storyboard Generator] 가동...")
    
    storyboard = {
        "video_title": "🍫 두바이 초콜릿: 그 바삭함의 비밀 (The Science of Crunch)",
        "theme": "Cinematic & Educational",
        "aspect_ratio": "9:16 (Shorts)",
        "scenes": [
            {
                "scene_number": 1,
                "visual_prompt": "Cinematic extreme macro shot of a knife slowly slicing through a thick Dubai chocolate bar. The shell cracks perfectly. Dramatic side lighting, dark background, 8K, highly detailed texture.",
                "voiceover": "요즘 난리난 이 소리, 들리시나요? 두바이 초콜릿의 핵심, 바로 '카다이프'의 바삭함입니다.",
                "style": {
                    "bg_color": "#1A1A1A",
                    "text_color": "#FFD700",
                    "font": "Pretendard-Bold"
                },
                "motion": "Slow Motion Zoom-in (Dolly shot)"
            },
            {
                "scene_number": 2,
                "visual_prompt": "Extreme close-up of golden, toasted knafeh noodles (Kadayif) being tossed in a frying pan with sizzling butter. Golden sparks, warm lighting, cinematic smoke.",
                "voiceover": "중동의 전통 국수 카다이프를 버터에 볶아 극강의 바삭함을 만들어내죠. 이게 바로 식감의 비밀입니다.",
                "style": {
                    "bg_color": "#2D1B0D",
                    "text_color": "#FFFFFF",
                    "font": "Pretendard-Medium"
                },
                "motion": "Pan Right to Left"
            },
            {
                "scene_number": 3,
                "visual_prompt": "Macro shot of vibrant, neon-green pistachio cream being mixed with the crispy golden noodles. The contrast of green and gold is mesmerizing. Professional food photography lighting.",
                "voiceover": "여기에 진한 피스타치오 크림을 듬뿍 섞어주면, 우리가 아는 그 마법의 단면이 완성됩니다.",
                "style": {
                    "bg_color": "#0F2D0F",
                    "text_color": "#E0FFE0",
                    "font": "Pretendard-Bold"
                },
                "motion": "Rotating Top-down shot"
            },
            {
                "scene_number": 4,
                "visual_prompt": "A person taking a bite of the chocolate, their face showing pure bliss. The background is a blurred high-end cafe. Soft bokeh, warm atmosphere.",
                "voiceover": "단순한 유행이 아닙니다. 식감과 풍미의 완벽한 조화, 직접 경험해보세요.",
                "style": {
                    "bg_color": "#1A1A1A",
                    "text_color": "#FFD700",
                    "font": "Pretendard-Bold"
                },
                "motion": "Slow Zoom-out"
            }
        ],
        "audio_plan": {
            "bgm": "Luxury Cinematic Lo-fi",
            "voice_actor": "ko-KR-SunHiNeural (Elegant & Calm)",
            "ducking": "Lower BGM by 80% during Voiceover"
        }
    }
    
    # JSON 파일로 저장
    output_file = "vids_chocolate_storyboard.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(storyboard, f, indent=2, ensure_ascii=False)
        
    print(f"\n✨ 스토리보드 생성 완료: {output_file}")
    
    # 화면에 보기 좋게 출력
    print("\n" + "="*50)
    print(f"🎥 {storyboard['video_title']}")
    print("="*50)
    for scene in storyboard["scenes"]:
        print(f"\n[Scene {scene['scene_number']}]")
        print(f"🎨 Visual: {scene['visual_prompt'][:80]}...")
        print(f"🎙️ Script: {scene['voiceover']}")
        print(f"🎬 Motion: {scene['motion']}")
    print("\n" + "="*50)
    print(f"🎵 Audio: {storyboard['audio_plan']['bgm']} (Ducking Enabled)")
    print("="*50)

if __name__ == "__main__":
    generate_chocolate_storyboard()
