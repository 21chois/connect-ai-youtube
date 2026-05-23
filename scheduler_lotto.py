import schedule
import time
import datetime
from run_lotto_cat_v2 import main as lotto_job

def job():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{now}] ⏰ 스케줄러: 오늘의 냥도사 로또 영상 제작 및 업로드 시작!")
    try:
        lotto_job()
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ 오늘의 작업 완료.")
    except Exception as e:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 작업 중 에러 발생: {e}")

# 매일 오후 5시 (17:00)에 실행
schedule.every().day.at("17:00").do(job)

print("=" * 60)
print("🐾 냥도사 로또 자동 업로드 스케줄러가 실행되었습니다.")
print(f"설정 시간: 매일 오후 05:00 (KST)")
print(f"현재 시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("이 창을 닫지 말고 켜두시면 매일 자동으로 업로드됩니다.")
print("=" * 60)

# 테스트용 (지금 바로 한 번 실행해보고 싶다면 아래 주석을 해제하세요)
# job()

while True:
    schedule.run_pending()
    time.sleep(60) # 1분마다 체크
