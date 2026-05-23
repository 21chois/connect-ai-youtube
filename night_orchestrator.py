import time
import subprocess
import os
from datetime import datetime

def run_script(script_name):
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Executing: {script_name}")
    try:
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        result = subprocess.run(["python", script_name], env=env, check=True)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Success: {script_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Failed: {script_name} (Exit code: {e.returncode})")
        return False

def main():
    print("=" * 60)
    print("Agent Young-sik: Night Mode Orchestrator Started")
    print("Goal: 4 High-Quality Videos (Lotto, Kaimak, Commerce, Dubai)")
    print("=" * 60)

    # 1. 냥도사 V3 (감성 스토리텔링) - 23:00 실행
    run_script("run_lotto_cat_v3.py")

    # 2시간 대기 (유튜브 알고리즘 및 쿼터 관리)
    print("\nWaiting 2 hours for the next slot...")
    time.sleep(2 * 3600)

    # 2. 카이막 스페셜 (Kaimak) - 01:00 실행
    run_script("run_kaimak_special.py")

    # 2시간 대기
    print("\nWaiting 2 hours for the next slot...")
    time.sleep(2 * 3600)

    # 3. 커머스 트렌드 (Commerce) - 03:00 실행
    run_script("run_commerce_trend_v1.py")

    # 2시간 대기
    print("\nWaiting 2 hours for the final slot...")
    time.sleep(2 * 3600)

    # 4. 두바이 초콜릿 데일리 (Dubai Chocolate) - 05:00 실행
    run_script("run_dubai_chocolate_daily.py")

    print("\n" + "=" * 60)
    print("All Night Tasks Completed! Good Morning, User.")
    print("=" * 60)

if __name__ == "__main__":
    main()
