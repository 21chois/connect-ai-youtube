import os
import sys
import time
import schedule
from datetime import datetime
from dotenv import load_dotenv

# [설정] 프로젝트 루트 경로 확보
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, ".agent", "tools"))

# 환경 변수 로드
load_dotenv(os.path.join(BASE_DIR, ".env"))

# 개별 에이전트 미션 임포트
try:
    from run_dubai_chocolate_daily import generate_and_upload_chocolate as run_chocolate
    from run_kaimak_special import main as run_kaimak
    from run_lotto_cat import generate_and_upload_lotto_cat as run_lotto
except ImportError as e:
    print(f"❌ 임포트 실패: {e}")
    sys.exit(1)

def job_wrapper(func, name, *args, **kwargs):
    print(f"\n{'='*60}")
    print(f"🚀 [Connect AI] 미션 시작: {name} ({datetime.now().strftime('%H:%M:%S')})")
    print(f"{'='*60}")
    try:
        func(*args, **kwargs)
        print(f"✅ [Connect AI] 미션 완료: {name}")
    except Exception as e:
        print(f"❌ [Connect AI] 미션 에러 ({name}): {e}")

def main():
    print("╔══════════════════════════════════════════════════════╗")
    print("║   🏢 Connect AI | Mega Orchestrator (V1.0)           ║")
    print("║   - 총괄 관리: 조감독 영식 (Agent Young-sik)         ║")
    print("║   - 운영 채널: 메인(초콜릿), 서브(카이막/로또)       ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("스케줄러 대기 중...\n")

    # 1. 데일리 스케줄 등록 (24시간 자동 주행)
    # 12:00 - 두바이 초콜릿 시리즈 (메인 채널)
    schedule.every().day.at("12:00").do(job_wrapper, run_chocolate, "두바이 초콜릿", time_slot="12:00", account_id="main")
    
    # 15:00 - 카이막 스페셜 (서브 채널)
    schedule.every().day.at("15:00").do(job_wrapper, run_kaimak, "카이막 스페셜")
    
    # 19:00 - 영험한 냥도사 로또 (서브 채널)
    schedule.every().day.at("19:00").do(job_wrapper, run_lotto, "냥도사 로또", account_id="sub")

    # [테스트용] 즉시 실행 (생성 점검 모드)
    job_wrapper(run_chocolate, "두바이 초콜릿(즉시 실행)", time_slot="Check", account_id="main")
    # job_wrapper(run_kaimak, "카이막(테스트)")

    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
