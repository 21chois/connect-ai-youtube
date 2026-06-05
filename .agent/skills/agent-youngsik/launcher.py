import os
import sys
import subprocess

# [설정] 상위 루트 경로 확보
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SKILL_DIR, "..", "..", ".."))

def run_script(script_name):
    script_path = os.path.join(ROOT_DIR, script_name)
    if not os.path.exists(script_path):
        print(f"❌ 파일을 찾을 수 없습니다: {script_path}")
        return
    
    print(f"🚀 실행 중: {script_name} (from Root: {ROOT_DIR})")
    # ROOT_DIR을 CWD로 설정하여 실행 (순차 실행을 위해 subprocess.run 사용)
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=ROOT_DIR,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ 실행 완료: {script_name}")
        else:
            print(f"⚠️ 실행 종료 (리턴코드: {result.returncode}): {script_name}")
    except Exception as e:
        print(f"❌ 실행 에러: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 인자로 받은 스크립트 실행
        target_script = sys.argv[1]
        run_script(target_script)
    else:
        # 인자가 없으면 기본적으로 제주 로또 실행 (하위 호환)
        run_script("run_lotto_jeju_olle.py")
