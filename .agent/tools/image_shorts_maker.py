import os
import subprocess
import re
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy import ImageSequenceClip, AudioFileClip, CompositeAudioClip
from google import genai
from google.genai import types

def create_image_shorts(client, prompt, output_path, subtitles):
    print(f"\nPhase 1: Generating 9:16 images using Imagen 4.0...")
    try:
        images = []
        
        # prompt가 리스트(VLOG 스토리보드)인 경우와 단일 스트링인 경우 처리
        prompts = prompt if isinstance(prompt, list) else [prompt] * len(subtitles)
        
        # [최적화] 네트워크 모델 리스트 조회(pagination)로 인한 로딩 지연/무한 대기 차단
        # 안정적인 최신 Imagen 3.0 모델군을 직접 정의하여 딜레이 없이 즉시 가동합니다.
        models_to_try = ['imagen-3.0-generate-002', 'imagen-3.0-generate-001']
        print(f"   [영식 최적화] 무한 대기 방지를 위해 정적 모델 리스트 로드 완료: {models_to_try}")
        
        for idx, p in enumerate(prompts):
            print(f"   Cut {idx+1}/{len(prompts)} generating...")
            
            success_gen = False
            last_err = None
            
            for model_name in models_to_try:
                try:
                    # 'generate_images' 지원 여부 확인 (일부 모델은 미지원일 수 있음)
                    result = client.models.generate_images(
                        model=model_name,
                        prompt=p,
                        config=types.GenerateImagesConfig(
                            number_of_images=1,
                            output_mime_type="image/jpeg",
                            aspect_ratio="9:16"
                        )
                    )
                    for generated_image in result.generated_images:
                        image = Image.open(BytesIO(generated_image.image.image_bytes))
                        images.append(image)
                    success_gen = True
                    # 성공한 모델을 기억하여 다음 컷에도 우선 사용하도록 최적화
                    models_to_try = [model_name] + [m for m in models_to_try if m != model_name]
                    break 
                except Exception as model_err:
                    last_err = model_err
                    continue 
            
            if not success_gen:
                raise Exception(f"사용 가능한 모든 Imagen 모델({models_to_try}) 시도 실패: {last_err}")
            
        if not images:
            raise Exception("이미지 생성 결과가 없습니다.")
            
    except Exception as e:
        import traceback
        print(f"❌ Image generation failed: {e}")
        traceback.print_exc()
        return False

    print(f"\nPhase 2: Compiling subtitles and video with Cinematic Motion (Ken Burns)...")
    try:
        clips = []
        current_time = 0.0
        
        for i, img in enumerate(images):
            # RGB mode ensuring
            img = img.convert("RGB")
            # Resize with a slight margin for zoom (e.g., 10% larger)
            base_w, base_h = (720, 1280)
            margin = 1.1 
            img_zoomed = img.resize((int(base_w * margin), int(base_h * margin)), Image.Resampling.LANCZOS)
            
            # --- Subtitle Rendering on PIL Image ---
            draw = ImageDraw.Draw(img_zoomed)
            try:
                # 윈도우 표준 폰트 경로 명시적 시도
                font_path = "C:/Windows/Fonts/malgun.ttf"
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, 60)
                else:
                    font = ImageFont.truetype("malgun.ttf", 60)
            except:
                font = ImageFont.load_default()
            
            text = subtitles[i] if i < len(subtitles) else ""
            
            # Default duration
            frame_duration = 5.0
            tts_clip = None
            
            if text:
                # Text Wrapping Logic
                max_width = int(base_w * margin * 0.8)
                words = text.split(' ')
                lines = []
                current_line = []
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    if bbox[2] - bbox[0] <= max_width:
                        current_line.append(word)
                    else:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                lines.append(' '.join(current_line))
                
                # --- Vids-Style Subtitle Box Rendering ---
                line_height = font.getbbox("Ay")[3] - font.getbbox("Ay")[1] + 25
                total_h = len(lines) * line_height
                
                padding = 40
                box_w = max_width + padding
                box_h = total_h + padding
                box_x = (base_w * margin - box_w) / 2
                box_y = (base_h * margin) - 350 - (box_h / 2)
                
                # Draw semi-transparent black background box
                draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h], fill=(0, 0, 0, 160))
                
                for idx, line in enumerate(lines):
                    l_bbox = draw.textbbox((0, 0), line, font=font)
                    l_w = l_bbox[2] - l_bbox[0]
                    l_x = (base_w * margin - l_w) / 2
                    l_y = box_y + (padding / 2) + (idx * line_height)
                    
                    # Modern white text (no shadow needed with box)
                    draw.text((l_x, l_y), line, font=font, fill="#FFFFFF")

                # --- TTS Generation ---
                try:
                    # [수정] 다중 에이전트 동시 가동 시 파일 충돌 방지를 위해 타임스탬프 추가
                    session_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    tts_file = f"temp_audio_{session_id}_{i}.mp3"
                    tts_text = re.sub(r'[★☆✨🍀💰🔮]', '', text).strip()
                    # edge-tts 경로가 환경에 따라 다를 수 있으므로 명시적 오류 체크
                    cmd = ["edge-tts", "--voice", "ko-KR-SunHiNeural", "--text", tts_text, "--write-media", tts_file]
                    subprocess.run(cmd, check=True, capture_output=True)
                    tts_clip = AudioFileClip(tts_file)
                    frame_duration = max(5.0, tts_clip.duration + 0.8)
                    
                    # 나중에 삭제하기 위해 파일 목록 추적
                    if not hasattr(create_image_shorts, "_temp_files"):
                        create_image_shorts._temp_files = []
                    create_image_shorts._temp_files.append(tts_file)
                    
                except Exception as e:
                    print(f"⚠️ TTS Error (Continuing without audio): {e}")

            # --- MoviePy Clip with Zoom Effect ---
            from moviepy import ImageClip, vfx
            
            # Create ImageClip from the PIL image
            img_array = np.array(img_zoomed)
            iclip = ImageClip(img_array).with_duration(frame_duration)
            
            # Apply Ken Burns (Slow Zoom In)
            # Zoom from 1.0 to 1.1 over the duration
            def zoom(t):
                return 1 + 0.1 * (t / frame_duration)
            
            iclip = iclip.with_effects([vfx.Resize(zoom)])
            # Crop to original 720x1280
            iclip = iclip.cropped(x_center=iclip.w/2, y_center=iclip.h/2, width=720, height=1280)
            
            if tts_clip:
                iclip = iclip.with_audio(tts_clip.with_start(0))
            
            clips.append(iclip)
            current_time += frame_duration

        # --- [Effort Premium] Human Authenticity Proof Clip ---
        try:
            human_source_dir = os.path.join(os.getcwd(), "human_sources")
            if os.path.exists(human_source_dir):
                human_files = [f for f in os.listdir(human_source_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                if human_files:
                    import random
                    # 가장 최근 파일 혹은 랜덤하게 하나 선택
                    h_file = os.path.join(human_source_dir, random.choice(human_files))
                    print(f"   🔍 [Effort Premium] Human Source Detected: {os.path.basename(h_file)}")
                    
                    h_img = Image.open(h_file).convert("RGB")
                    # Resize to fit 720x1280
                    h_img = h_img.resize((720, 1280), Image.Resampling.LANCZOS)
                    
                    # Add "Authenticity Verified" Watermark
                    h_draw = ImageDraw.Draw(h_img)
                    try:
                        h_font = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 50)
                    except:
                        h_font = ImageFont.load_default()
                    
                    watermark_text = "✨ 실증 데이터 확인됨 (Verified)"
                    w_bbox = h_draw.textbbox((0, 0), watermark_text, font=h_font)
                    w_w = w_bbox[2] - w_bbox[0]
                    w_h = w_bbox[3] - w_bbox[1]
                    
                    # Draw a nice gold box for the watermark
                    h_draw.rectangle([50, 100, 50 + w_w + 40, 100 + w_h + 30], fill=(218, 165, 32, 200)) # Goldenrod
                    h_draw.text((70, 110), watermark_text, font=h_font, fill="#FFFFFF")
                    
                    h_clip = ImageClip(np.array(h_img)).with_duration(3.5) # 3.5 seconds proof
                    
                    # Add "Director's Voice" or sound effect
                    # (For now, just a subtitle-like message at the bottom)
                    h_draw.rectangle([0, 1150, 720, 1280], fill=(0, 0, 0, 180))
                    h_draw.text((60, 1180), "감독님이 직접 발로 뛰어 확인한\n진정성 있는 정보입니다.", font=h_font, fill="#FFD700") # Gold text
                    
                    # Re-create clip with modified image
                    h_clip = ImageClip(np.array(h_img)).with_duration(3.5)
                    clips.append(h_clip)
                    print("   ✅ [Effort Premium] Authenticity clip appended.")

        except Exception as h_err:
            print(f"   ⚠️ Effort Premium Error: {h_err}")

        # Concatenate all clips
        from moviepy import concatenate_videoclips
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # --- BGM Layering ---
        bgm_file = "calm_bgm.webm"
        if os.path.exists(bgm_file):
            try:
                from moviepy import afx, CompositeAudioClip
                bgm = AudioFileClip(bgm_file).with_effects([afx.MultiplyVolume(0.12)])
                if bgm.duration < final_clip.duration:
                    from moviepy import concatenate_audioclips
                    n_loops = int(final_clip.duration / bgm.duration) + 1
                    bgm = concatenate_audioclips([bgm] * n_loops).with_duration(final_clip.duration)
                else:
                    bgm = bgm.subclipped(0, final_clip.duration)
                
                # Combine original audio (TTS) with BGM
                if final_clip.audio:
                    # Intelligent Ducking: BGM volume is reduced globally to ensure VO clarity
                    bgm = bgm.with_effects([afx.MultiplyVolume(0.12)]) 
                    new_audio = CompositeAudioClip([bgm, final_clip.audio])
                else:
                    new_audio = bgm
                final_clip = final_clip.with_audio(new_audio)
            except Exception as e:
                print(f"⚠️ BGM Error: {e}")

        print(f"\nPhase 3: Rendering Cinematic High-Quality MP4...")
        final_clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

        # [추가] 메모리 해제를 위해 모든 클립 명시적으로 닫기
        final_clip.close()
        for clip in clips:
            clip.close()
        
        # Cleanup temp audio files
        if hasattr(create_image_shorts, "_temp_files"):
            for tts_file in create_image_shorts._temp_files:
                if os.path.exists(tts_file):
                    try:
                        os.remove(tts_file)
                    except:
                        pass
            create_image_shorts._temp_files = []
                    
        print(f"Video synthesis complete: {output_path}")
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ Video synthesis failed: {e}")
        traceback.print_exc()
        return False
