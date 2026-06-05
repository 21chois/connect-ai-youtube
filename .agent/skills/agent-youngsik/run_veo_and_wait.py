import os
import time
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# [설정] 프로젝트 루트 확보
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

def run_veo_complete():
    print("🚀 [Veo 3.1] 통합 제작 및 자동 다운로드 프로세스 시작")
    
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    # 기존 작업이 있는지 확인
    op_file = "veo_op_id.txt"
    op_name = None
    if os.path.exists(op_file):
        with open(op_file, "r") as f:
            op_name = f.read().strip()
            print(f"🔄 기존 작업({op_name})을 이어받아 상태를 확인합니다.")

    if not op_name:
        print(f"🎬 새로운 영상 생성 요청 중: '{prompt}'")
        try:
            operation = client.models.generate_videos(
                model="veo-3.1-generate-preview",
                prompt=prompt,
                config=types.GenerateVideosConfig(
                    aspect_ratio="9:16",
                    resolution="720p",
                ),
            )
            op_name = operation.name
            with open(op_file, "w") as f:
                f.write(op_name)
            print(f"📌 새 작업 ID 저장 완료: {op_name}")
        except Exception as e:
            print(f"❌ 생성 요청 실패: {e}")
            return
    
    # 작업 객체 가져오기
    try:
        operation = client.operations.get(op_name)
    except Exception as e:
        print(f"❌ 작업을 불러올 수 없습니다: {e}")
        # 파일 삭제 후 재시작 유도
        if os.path.exists(op_file): os.remove(op_file)
        return
        
        print("\n⏳ 영상 제작 중입니다... (약 3~5분 소요)")
        print("💡 터미널을 끄지 말고 기다려 주세요. 완료 시 자동으로 다운로드됩니다.")
        
        start_time = time.time()
        while not operation.done:
            # 15초마다 상태 업데이트
            elapsed = int(time.time() - start_time)
            print(f"\r   > 진행 중... ({elapsed}초 경과)", end="", flush=True)
            time.sleep(15)
            operation = client.operations.get(op_name)
            
        print("\n\n✨ 영상 제작 완료!")
        
        if operation.response and hasattr(operation.response, 'generated_videos'):
            video_file = operation.response.generated_videos[0].video
            output_name = "veo_final_result.mp4"
            
            print(f"📥 결과물 다운로드 중...")
            # SDK의 get_content 또는 download 사용
            content = client.files.get_content(file=video_file.name)
            with open(output_name, "wb") as f:
                f.write(content)
                
            print(f"✅ 모든 작업 대성공! 파일 확인: {os.path.abspath(output_name)}")
        else:
            print("❌ 영상 생성에 실패했거나 결과가 없습니다.")
            
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")

if __name__ == "__main__":
    run_veo_complete()
