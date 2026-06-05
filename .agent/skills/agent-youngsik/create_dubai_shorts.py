import os
import sys
from PIL import Image
from datetime import datetime

# Add the tools directory to path
# We are in .agent/skills/agent-youngsik/
ROOT_DIR = os.path.abspath(os.path.join(os.getcwd(), "..", "..", ".."))
TOOLS_DIR = os.path.join(ROOT_DIR, ".agent", "tools")
sys.path.append(TOOLS_DIR)

import subprocess
import re
import numpy as np
from moviepy import ImageClip, vfx, AudioFileClip, CompositeAudioClip, concatenate_videoclips
from PIL import ImageDraw, ImageFont

def create_shorts_from_images(image_paths, output_path, subtitles):
    print(f"\nPhase: Synthesizing Video from existing images...")
    try:
        clips = []
        for i, img_path in enumerate(image_paths):
            print(f"   Processing image {i+1}/{len(image_paths)}: {os.path.basename(img_path)}")
            img = Image.open(img_path).convert("RGB")
            base_w, base_h = (720, 1280)
            img = img.resize((720, 1280), Image.Resampling.LANCZOS)
            margin = 1.1 
            img_zoomed = img.resize((int(base_w * margin), int(base_h * margin)), Image.Resampling.LANCZOS)
            
            draw = ImageDraw.Draw(img_zoomed)
            try:
                font_path = "C:/Windows/Fonts/malgunbd.ttf"
                if not os.path.exists(font_path): font_path = "C:/Windows/Fonts/malgun.ttf"
                font = ImageFont.truetype(font_path, 60)
            except: font = ImageFont.load_default()
            
            text = subtitles[i] if i < len(subtitles) else ""
            frame_duration = 5.0
            tts_clip = None
            
            if text:
                max_width = int(base_w * margin * 0.8)
                words = text.split(' ')
                lines = []
                current_line = []
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    if bbox[2] - bbox[0] <= max_width: current_line.append(word)
                    else:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                lines.append(' '.join(current_line))
                
                line_height = font.getbbox("Ay")[3] - font.getbbox("Ay")[1] + 25
                total_h = len(lines) * line_height
                start_y = (base_h * margin) - 350 - (total_h / 2)
                for idx, line in enumerate(lines):
                    l_bbox = draw.textbbox((0, 0), line, font=font)
                    l_w, l_y_off = l_bbox[2] - l_bbox[0], start_y + (idx * line_height)
                    l_x = (base_w * margin - l_w) / 2
                    for dx, dy in [(-3,-3), (3,-3), (-3,3), (3,3)]: draw.text((l_x+dx, l_y_off+dy), line, font=font, fill="black")
                    draw.text((l_x, l_y_off), line, font=font, fill="#FFD700")

                try:
                    session_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    tts_file = f"temp_audio_{session_id}_{i}.mp3"
                    tts_text = re.sub(r'[★☆✨🍀💰🔮]', '', text).strip()
                    subprocess.run(["edge-tts", "--voice", "ko-KR-SunHiNeural", "--text", tts_text, "--write-media", tts_file], check=True, capture_output=True)
                    tts_clip = AudioFileClip(tts_file)
                    frame_duration = max(5.0, tts_clip.duration + 0.8)
                except Exception as e: print(f"   ⚠️ TTS Error: {e}")

            img_array = np.array(img_zoomed)
            iclip = ImageClip(img_array).with_duration(frame_duration)
            iclip = iclip.with_effects([vfx.Resize(lambda t: 1 + 0.08 * (t / frame_duration))])
            iclip = iclip.cropped(x_center=iclip.w/2, y_center=iclip.h/2, width=720, height=1280)
            if tts_clip: iclip = iclip.with_audio(tts_clip.with_start(0))
            clips.append(iclip)

        final_clip = concatenate_videoclips(clips, method="compose")
        bgm_path = os.path.join(ROOT_DIR, "calm_bgm.webm")
        if os.path.exists(bgm_path):
            from moviepy import afx
            bgm = AudioFileClip(bgm_path).with_effects([afx.MultiplyVolume(0.15)])
            if bgm.duration < final_clip.duration:
                from moviepy import concatenate_audioclips
                bgm = concatenate_audioclips([bgm] * (int(final_clip.duration / bgm.duration) + 1)).with_duration(final_clip.duration)
            else: bgm = bgm.subclipped(0, final_clip.duration)
            final_clip.audio = CompositeAudioClip([bgm, final_clip.audio]) if final_clip.audio else bgm

        final_clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
        final_clip.close()
        for clip in clips: clip.close()
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # 대표님이 생성한 고화질 이미지 4장 경로
    brain_dir = r"C:\Users\user\.gemini\antigravity\brain\632594f5-6fec-482e-8d24-9d8d7b803c70"
    images = [
        os.path.join(brain_dir, "chocolate_scene_1_crack_1778794980904.png"),
        os.path.join(brain_dir, "chocolate_scene_2_kadayif_1778794993804.png"),
        os.path.join(brain_dir, "chocolate_scene_3_mixing_1778795008013.png"),
        os.path.join(brain_dir, "chocolate_scene_4_eating_1778795024629.png")
    ]
    subs = [
        "요즘 난리난 이 소리, 들리시나요? 두바이 초콜릿의 핵심은 바삭함입니다! 🍫",
        "중동 전통 카다이프를 버터에 볶아 극강의 식감을 완성했죠. ✨",
        "여기에 진한 피스타치오 크림이 섞이면... 이게 바로 마법의 단면입니다! 💚",
        "단순한 유행이 아닌, 맛의 조화. 지금 바로 경험해보세요! 💎"
    ]
    output_dir = os.path.join(ROOT_DIR, "output_assets")
    os.makedirs(output_dir, exist_ok=True)
    output = os.path.join(output_dir, f"dubai_final_shorts.mp4")
    create_shorts_from_images(images, output, subs)
