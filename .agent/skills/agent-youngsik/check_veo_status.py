import os
import time
from dotenv import load_dotenv
from google import genai

# [설정] 프로젝트 루트 확보
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", ".."))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

def check_and_download():
    print("🔍 [Veo 3.1] 생성 상태 확인 및 다운로드 중...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    # 최근 실행된 작업 목록 가져오기 (가장 최근 것 확인)
    try:
        # Note: 실제 환경에서는 operation ID를 저장해두고 추적하는 것이 좋음
        # 여기서는 가장 최근에 생성된 비디오 파일을 찾거나 operations 리스트를 조회 시도
        operations = client.operations.list()
        target_op = None
        for op in operations:
            if not op.done:
                target_op = op
                break
        
        if not target_op:
            # 만약 진행 중인 게 없다면 가장 최근 완료된 것 확인
            for op in operations:
                target_op = op
                break

        if target_op:
            print(f"⌛ 작업 상태: {'완료' if target_op.done else '진행 중'}")
            if target_op.done:
                if target_op.response and hasattr(target_op.response, 'generated_videos'):
                    video_file = target_op.response.generated_videos[0].video
                    output_name = "veo_test_result.mp4"
                    # 다운로드 및 저장
                    # client.files.download 는 File 객체를 인자로 받음
                    # 만약 직접 저장이 안되면 바이트를 읽어서 저장
                    print(f"📥 영상 다운로드 중: {output_name}")
                    # SDK 버전에 따라 다를 수 있으나 일반적인 패턴:
                    content = client.files.get_content(file=video_file.name)
                    with open(output_name, "wb") as f:
                        f.write(content)
                    print(f"✅ 다운로드 완료! {os.path.abspath(output_name)}")
                else:
                    print("❌ 영상 생성 결과가 없습니다. (에러 또는 취소)")
            else:
                print("⏳ 아직 생성 중입니다. 1~2분 후 다시 실행해 주세요.")
        else:
            print("❌ 최근 실행된 Veo 작업을 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"❌ 상태 확인 중 에러 발생: {e}")

if __name__ == "__main__":
    check_and_download()
