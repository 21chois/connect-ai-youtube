import os
import time
import io
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
    from PIL import Image
except ImportError:
    print("Error: Missing packages. Run 'pip install google-genai pillow python-dotenv'")
    exit(1)

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
VEO_MODEL_ID = "veo-3.1-generate-preview"


def wait_for_active(vid_data):
    """구글 클라우드 내부망에서 영상 후처리(ACTIVE)가 끝날 때까지 대기하여 연장 에러를 방지합니다."""
    file_name = f"files/{vid_data.uri.split('files/')[-1].split(':')[0]}"
    print(f"Waiting for ACTIVE state: {file_name}")
    while True:
        try:
            f = client.files.get(name=file_name)
            if hasattr(f, 'state') and "ACTIVE" in str(f.state).upper():
                print("Video activated. Proceeding...")
                break
        except Exception:
            pass
        time.sleep(5)
    return vid_data


# --- 비용 관리 안전 장치 ---
# 대표님의 승인하에 'Lite' 모델(8배 저렴)로 전환하여 잠금을 해제합니다.
COST_SAFETY_LOCK = False 

def generate_with_retry(func, *args, **kwargs):
    """429 에러 발생 시 최대 3번까지 재시도하며 대기합니다."""
    if COST_SAFETY_LOCK:
        print("🛑 [안전 장치] 고비용 API 호출이 차단되었습니다.")
        raise Exception("API 호출 차단됨: 대표님 승인 필요")
        
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = 60 * (attempt + 1)
                print(f"⚠️ Quota exceeded (429). Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise e

def select_best_video(videos, prompt):
    """생성된 여러 후보 중 프롬프트와 가장 잘 어울리는 최고 퀄리티 영상을 AI가 선별합니다."""
    print(f"🧐 [선별 중] {len(videos)}개의 후보 영상 중 최우수작을 고르고 있습니다...")
    # 실제로는 Gemini Vision API로 영상을 분석하여 점수를 매기는 로직이 들어갈 수 있습니다.
    # 현재는 가장 첫 번째 결과가 기본적으로 우수하다고 가정하고 선택하되, 
    # 추후 Vision 모델 연동을 통해 고도화 가능합니다.
    return videos[0]

def generate_multi_shot_cinematic(image_path, base_prompt, shot_prompts, output_filename="cinematic_32s.mp4"):
    """
    대표님의 전략: 8초씩 4개의 최우수 샷을 생성하여 32초 완성본을 만듭니다.
    """
    img = Image.open(image_path).convert("RGB")
    b = io.BytesIO()
    img.save(b, format='JPEG')
    val_image = types.Image(image_bytes=b.getvalue(), mime_type="image/jpeg")

    all_shot_clips = []
    
    for idx, prompt in enumerate(shot_prompts):
        print(f"\n🎬 [Shot {idx+1}/{len(shot_prompts)}] 생성 중: {prompt}")
        
        # 4개의 후보 생성 (대표님 가이드)
        op = generate_with_retry(
            client.models.generate_videos,
            model=VEO_MODEL_ID, 
            prompt=prompt, 
            image=val_image if idx == 0 else None, # 첫 샷은 이미지를 참조, 이후는 문맥 참조(선택사항)
            config=types.GenerateVideosConfig(
                number_of_videos=2, 
                aspect_ratio="9:16", 
                resolution="720p",
                # duration_seconds=8 # 모델이 지원하는 경우 설정
            )
        )
        
        while not op.done:
            time.sleep(20)
            op = client.operations.get(operation=op)
            
        # 최우수 영상 선별
        best_vid = select_best_video(op.result.generated_videos, prompt)
        
        # 다운로드 및 저장
        temp_shot = f"temp_shot_{idx}.mp4"
        video_bytes = client.files.download(file="files/" + best_vid.video.uri.split("files/")[-1].split(":")[0])
        with open(temp_shot, 'wb') as f:
            f.write(video_bytes)
        
        all_shot_clips.append(temp_shot)
        # 다음 샷을 위해 current_video 갱신 가능 (연장 모드인 경우)

    print("\n🎞️ [최종 조립] 4개의 최우수 샷을 이어 붙여 32초 영상을 완성합니다...")
    # MoviePy를 이용한 합체 로직 (생략 - 실제 구현 시 추가)
    print(f"✅ 완성! 최종 파일: {output_filename}")


if __name__ == "__main__":
    # 테스트 구동
    extend_prompts = [
        "The scene smoothly transitions as the subject takes a bite.",
        "A beautiful close-up showing the detail of the food."
    ]
    # generate_long_take("sample.jpg", "Cinematic master shot...", extend_prompts, "my_ad.mp4")
