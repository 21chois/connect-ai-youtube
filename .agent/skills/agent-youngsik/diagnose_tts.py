import subprocess
import os

def diagnose_tts():
    print("🔍 [TTS 진단] 시작...")
    
    # 1. edge-tts 명령어 존재 여부 확인
    try:
        result = subprocess.run(["edge-tts", "--list-voices"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ edge-tts 명령어가 시스템에서 인식됩니다.")
        else:
            print(f"❌ edge-tts 명령어가 에러를 반환합니다: {result.stderr}")
    except FileNotFoundError:
        print("❌ edge-tts 명령어를 찾을 수 없습니다. (환경변수 PATH 문제 또는 미설치)")
    except Exception as e:
        print(f"❌ 예기치 못한 에러: {e}")

    # 2. 직접 설치 시도 안내
    print("\n💡 해결 방법:")
    print("만약 위에서 ❌가 떴다면, 터미널에 다음을 입력하여 수동 설치해 주세요:")
    print("pip install edge-tts")
    
    # 3. 테스트 파일 생성 시도
    print("\n🔊 테스트 오디오 생성 시도 중...")
    test_file = "test_audio_check.mp3"
    try:
        cmd = ["edge-tts", "--voice", "ko-KR-SunHiNeural", "--text", "안녕하세요, 소리 테스트입니다.", "--write-media", test_file]
        subprocess.run(cmd, check=True)
        if os.path.exists(test_file):
            print(f"✅ 테스트 오디오 파일 생성 성공! ({test_file})")
            print("이 파일을 직접 재생해서 소리가 들리는지 확인해 보세요.")
        else:
            print("❌ 파일이 생성되지 않았습니다.")
    except Exception as e:
        print(f"❌ 오디오 생성 실패: {e}")

if __name__ == "__main__":
    diagnose_tts()
