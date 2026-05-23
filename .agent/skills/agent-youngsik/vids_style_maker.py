import os
import json
import subprocess
import re
import numpy as np
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, vfx, afx, ColorClip, CompositeVideoClip

# [경로 설정] 스크립트 위치 기준
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def render_vids_style(storyboard_path, output_path):
    print(f"🚀 [Vids-Style Rendering] 시작: {storyboard_path}", flush=True)
    
    if not os.path.isabs(storyboard_path):
        storyboard_path = os.path.join(SCRIPT_DIR, storyboard_path)
        
    if not os.path.exists(storyboard_path):
        print(f"❌ 스토리보드 파일을 찾을 수 없습니다: {storyboard_path}", flush=True)
        return

    with open(storyboard_path, "r", encoding="utf-8") as f:
        sb = json.load(f)
        
    clips = []
    
    # 폰트 설정
    font_path = "C:/Windows/Fonts/malgunbd.ttf"
    if not os.path.exists(font_path):
        font_path = "C:/Windows/Fonts/malgun.ttf"

    all_audio_clips = []
    for i, scene in enumerate(sb["scenes"]):
        print(f"🎬 Scene {i+1} 처리 중...", flush=True)
        
        img_w, img_h = 720, 1280
        image_path = scene.get("image_path")
        
        if image_path and os.path.exists(image_path):
            print(f"   🖼️ 이미지 로드 중: {os.path.basename(image_path)}", flush=True)
            img = Image.open(image_path).convert("RGB")
            img = img.resize((img_w, img_h), Image.Resampling.LANCZOS)
        else:
            print("   ⚠️ 이미지가 없어 배경색을 사용합니다.", flush=True)
            bg_color = scene.get("style", {}).get("bg_color", "#1A1A1A")
            h = bg_color.lstrip('#')
            rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
            img = Image.new("RGB", (img_w, img_h), color=rgb)
        
        # 2. TTS 생성
        tts_file = f"temp_tts_{i}.mp3"
        tts_text = re.sub(r'[^\w\s,.!?가-힣]', '', scene["voiceover"]).strip()
        try:
            print(f"   🎙️ TTS 생성 중: {tts_text[:20]}...", flush=True)
            cmd = ["edge-tts", "--voice", "ko-KR-SunHiNeural", "--text", tts_text, "--write-media", tts_file]
            subprocess.run(cmd, check=True, capture_output=True)
            audio = AudioFileClip(tts_file)
            all_audio_clips.append(audio) # 트래킹 시작
            duration = audio.duration + 1.0
        except Exception as e:
            print(f"   ⚠️ TTS 생성 실패 (Scene {i+1}): {e}", flush=True)
            audio = None
            duration = 5.0
            
        # 3. 비디오 클립 생성
        margin = 1.1
        img_zoomed = img.resize((int(img_w * margin), int(img_h * margin)), Image.Resampling.LANCZOS)
        
        iclip = ImageClip(np.array(img_zoomed)).with_duration(duration)
        
        if "Zoom-in" in scene.get("motion", ""):
            iclip = iclip.with_effects([vfx.Resize(lambda t: 1 + 0.1 * (t / duration))])
        elif "Zoom-out" in scene.get("motion", ""):
            iclip = iclip.with_effects([vfx.Resize(lambda t: 1.1 - 0.1 * (t / duration))])
            
        iclip = iclip.cropped(x_center=iclip.w/2, y_center=iclip.h/2, width=img_w, height=img_h)
        
        def add_subtitle_box(img_frame, text):
            pil_img = Image.fromarray(img_frame)
            draw = ImageDraw.Draw(pil_img, "RGBA")
            try:
                font = ImageFont.truetype(font_path, 45)
            except:
                font = ImageFont.load_default()
            
            max_w = img_w * 0.8
            words = text.split()
            lines, curr = [], ""
            for w in words:
                test = curr + " " + w if curr else w
                if draw.textbbox((0,0), test, font=font)[2] < max_w: curr = test
                else:
                    lines.append(curr)
                    curr = w
            lines.append(curr)
            
            line_h = font.getbbox("Ay")[3] - font.getbbox("Ay")[1] + 15
            box_w, box_h = max_w + 40, len(lines) * line_h + 40
            box_x, box_y = (img_w - box_w) / 2, img_h - box_h - 150
            draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h], fill=(0, 0, 0, 160))
            
            for idx, line in enumerate(lines):
                lw = draw.textbbox((0,0), line, font=font)[2]
                lx, ly = (img_w - lw) / 2, box_y + 20 + (idx * line_h)
                draw.text((lx, ly), line, font=font, fill=(255, 255, 255))
            return np.array(pil_img)

        iclip = iclip.transform(lambda get_frame, t: add_subtitle_box(get_frame(t), scene["voiceover"]))
        if audio: iclip = iclip.with_audio(audio)
        clips.append(iclip)

    final_video = concatenate_videoclips(clips, method="compose")
    
    # BGM 경로 수정 및 로딩
    bgm_path = os.path.join(os.path.dirname(SCRIPT_DIR), "..", "..", "calm_bgm.webm")
    if not os.path.exists(bgm_path):
        bgm_path = os.path.join(SCRIPT_DIR, "..", "..", "..", "calm_bgm.webm")
    
    bgm_clip = None
    if os.path.exists(bgm_path):
        print(f"   🎵 BGM 합성 중: {os.path.basename(bgm_path)}", flush=True)
        bgm_clip = AudioFileClip(bgm_path)
        all_audio_clips.append(bgm_clip) # BGM 트래킹
        
        if bgm_clip.duration < final_video.duration:
            from moviepy import concatenate_audioclips
            loop_count = int(final_video.duration / bgm_clip.duration) + 1
            bgm_clip = concatenate_audioclips([bgm_clip] * loop_count).with_duration(final_video.duration)
        else:
            bgm_clip = bgm_clip.subclipped(0, final_video.duration)
            
        bgm_clip = bgm_clip.with_effects([afx.MultiplyVolume(0.15)]) 
        final_video.audio = CompositeAudioClip([bgm_clip, final_video.audio]) if final_video.audio else bgm_clip

    print("🎥 최종 영상 렌더링 시작...", flush=True)
    try:
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
        print(f"✅ 완성: {output_path}", flush=True)
        
        final_path = os.path.join(SCRIPT_DIR, "vids_chocolate_FINAL.mp4")
        import shutil
        shutil.copy(output_path, final_path)
        print(f"📌 업로드용 최종본 복사 완료: {final_path}", flush=True)
        
    finally:
        # 모든 자원 명시적 해제
        try: final_video.close()
        except: pass
        for ac in all_audio_clips:
            try: ac.close()
            except: pass
        for vc in clips:
            try: vc.close()
            except: pass
        
        # 가비지 컬렉션 강제 실행 (WinError 6 방지 핵심)
        import gc
        gc.collect()
        
        # 임시 파일 삭제
        for i in range(len(sb["scenes"])):
            temp_file = f"temp_tts_{i}.mp3"
            if os.path.exists(temp_file):
                try: os.remove(temp_file)
                except: pass
        print("✨ 모든 리소스 해제 및 임시 파일 청소 완료", flush=True)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(SCRIPT_DIR, "..", "..", "..", ".env"))
    
    sb_path = "vids_chocolate_storyboard.json"
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    storage_base = os.getenv("STORAGE_BASE_PATH")
    if storage_base and os.path.exists(os.path.splitdrive(storage_base)[0]):
        out_dir = os.path.join(storage_base, "output_assets")
        os.makedirs(out_dir, exist_ok=True)
        output_name = os.path.join(out_dir, f"vids_chocolate_{timestamp}.mp4")
    else:
        output_name = f"vids_chocolate_{timestamp}.mp4"
        
    try:
        render_vids_style(sb_path, output_name)
    except Exception as e:
        print(f"❌ 렌더링 중 치명적 오류 발생: {e}", flush=True)

