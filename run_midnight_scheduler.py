import schedule
import time
import datetime
import subprocess
import os

def job():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{now}] 🌙 심야 자동화 작업 시작! (컴퓨터 유휴 시간 활용)")
    try:
        # night_orchestrator.py 실행 (로또 고양이 + 커머스 트렌드 2편)
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        subprocess.run(["python", "night_orchestrator.py"], env=env, check=True)
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ 심야 작업이 모두 완료되었습니다.")
    except Exception as e:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 심야 작업 중 에러 발생: {e}")

# 밤 11시(23:00)에 실행하도록 설정
schedule.every().day.at("23:00").do(job)

print("=" * 70)
print("🌙 [Agent 영식] 심야 전용 절전형 스케줄러가 가동되었습니다.")
print("목적: 낮 시간대 컴퓨터 리소스(CPU/RAM) 점유 방지 및 속도 저하 해결")
print(f"작업 시간: 매일 밤 23:00 (KST) 시작 ~ 익일 새벽 05:00~06:00 종료 예상")
print(f"현재 시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("주의: 이 창은 최소화(- 기호)해두시면 됩니다. 낮에는 CPU를 0%만 사용하며 대기합니다.")
print("=" * 70)

while True:
    schedule.run_pending()
    time.sleep(60) # 1분에 한 번씩만 시간을 확인하여 CPU 부하 거의 없음
