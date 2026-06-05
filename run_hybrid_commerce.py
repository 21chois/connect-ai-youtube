import os
import json
import time
import subprocess
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from moviepy import ImageClip, VideoFileClip, AudioFileClip, concatenate_videoclips, vfx, CompositeVideoClip

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "hybrid_commerce_config.json")
# C드라이브 용량 확보를 위해 D드라이브로 렌더링 경로 변경
OUTPUT_DIR = r"D:\유튜브_데이터_영식\output_assets" if os.path.exists(r"D:\유튜브_데이터_영식") else os.path.join(BASE_DIR, "output_assets")
HUMAN_SOURCE_DIR = os.path.join(BASE_DIR, "human_sources")

def create_tts(text, index):
    import re
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    tts_file = f"temp_tts_{session_id}_{index}.mp3"
    tts_text = re.sub(r'[★☆✨🍀💰🔮👇🛒]', '', text).strip()
    cmd = ["edge-tts", "--voice", "ko-KR-SunHiNeural", "--text", tts_text, "--write-media", tts_file]
    subprocess.run(cmd, check=True)
    return tts_file

def draw_subtitle(img_w, img_h, text):
    txt_img = Image.new('RGBA', (img_w, img_h), (0,0,0,0))
    draw = ImageDraw.Draw(txt_img)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 45) # 폰트 크기 감소 (60 -> 45)
    except:
        font = ImageFont.load_default()
    
    margin = int(img_w * 0.8)
    words = text.split(' ')
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= margin:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    
    line_height = 60 # 줄간격 축소 (80 -> 60)
    total_h = len(lines) * line_height
    padding = 40
    box_w = margin + padding
    box_h = total_h + padding
    box_x = (img_w - box_w) / 2
    box_y = img_h - 220 - (box_h / 2) # 위치 하향 조정 (350 -> 220)
    
    draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h], fill=(0, 0, 0, 160))
    for idx, line in enumerate(lines):
        l_bbox = draw.textbbox((0, 0), line, font=font)
        l_w = l_bbox[2] - l_bbox[0]
        l_x = (img_w - l_w) / 2
        l_y = box_y + (padding / 2) + (idx * line_height)
        draw.text((l_x, l_y), line, font=font, fill="#FFFFFF")
    
    return txt_img

def run_hybrid_pipeline():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    item = config["items"][0] # 핸드 믹서기 타겟
        
    print(f"🚀 [하이브리드 파이프라인] {item['name']} 렌더링 시작...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    clips = []
    temp_files = []
    
    try:
        # 1. AI Hook (0~1)
        # Using pre-generated local AI images to bypass Google API 404 Error
        ai_images = [
            r"C:\Users\user\.gemini\antigravity\brain\f389af04-c370-4b27-a488-8ea2e3c63972\hand_mixer_hook_1779007753437.png",
            r"C:\Users\user\.gemini\antigravity\brain\f389af04-c370-4b27-a488-8ea2e3c63972\hand_mixer_outro1_1779007768375.png",
            r"C:\Users\user\.gemini\antigravity\brain\f389af04-c370-4b27-a488-8ea2e3c63972\hand_mixer_outro2_1779007785869.png"
        ]
        
        print("🎨 사전 생성된 AI 후크 이미지 불러오는 중...")
        img = Image.open(ai_images[0]).convert("RGB").resize((720, 1280))
        sub_img = draw_subtitle(720, 1280, item["subtitles"][0])
        img.paste(sub_img, (0,0), sub_img)
        
        tts_file = create_tts(item["subtitles"][0], 0)
        temp_files.append(tts_file)
        audio = AudioFileClip(tts_file)
        clip = ImageClip(np.array(img)).with_duration(max(3.0, audio.duration + 0.5)).with_audio(audio)
        clips.append(clip)
            
        # 2. Real Human Source
        source_file = item.get("human_source", "신기한 테이프.mp4")
        print(f"🎥 실사 영상 소스 병합 중 ({source_file})...")
        video_path = os.path.join(HUMAN_SOURCE_DIR, source_file)
        if os.path.exists(video_path):
            real_clip = VideoFileClip(video_path)
            # Take up to 5 seconds
            real_clip = real_clip.subclipped(0, min(5, real_clip.duration))
            # 저작권 회피 세탁: 좌우반전, 배속, 소리제거
            real_clip = real_clip.with_effects([vfx.MirrorX(), vfx.MultiplySpeed(1.2)]).without_audio()
            # 세로(9:16) 비율로 중앙 크롭
            real_clip = real_clip.resized(height=1280).cropped(x_center=real_clip.w/2, y_center=1280/2, width=720, height=1280)
            
            tts_file = create_tts(item["subtitles"][1], 1)
            temp_files.append(tts_file)
            audio = AudioFileClip(tts_file)
            real_clip = real_clip.with_audio(audio)
            
            sub_img = draw_subtitle(720, 1280, item["subtitles"][1])
            mask = ImageClip(np.array(sub_img.split()[3]) / 255.0, is_mask=True)
            sub_clip = ImageClip(np.array(sub_img)).with_duration(real_clip.duration).with_mask(mask)
            
            real_clip = CompositeVideoClip([real_clip, sub_clip])
            clips.append(real_clip)
            
        # 3. AI Outro
        print("🎨 사전 생성된 AI 아웃트로 이미지 불러오는 중...")
        for i in range(2, 4):
            img = Image.open(ai_images[i-1]).convert("RGB").resize((720, 1280))
            sub_img = draw_subtitle(720, 1280, item["subtitles"][i])
            img.paste(sub_img, (0,0), sub_img)
            
            tts_file = create_tts(item["subtitles"][i], i)
            temp_files.append(tts_file)
            audio = AudioFileClip(tts_file)
            
            clip = ImageClip(np.array(img)).with_duration(max(3.0, audio.duration + 0.5)).with_audio(audio)
            clips.append(clip)

        final_clip = concatenate_videoclips(clips, method="compose")
        out_path = os.path.join(OUTPUT_DIR, f"hybrid_{item['id']}_{int(time.time())}.mp4")
        print("🎬 렌더링 시작...")
        final_clip.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac")
        
        print(f"✅ 하이브리드 파이프라인 완성: {out_path}")
        
    finally:
        for f in temp_files:
            if os.path.exists(f): 
                try: os.remove(f)
                except: pass

if __name__ == "__main__":
    run_hybrid_pipeline()
