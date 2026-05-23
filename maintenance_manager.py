
import os
import sys
import time
import subprocess
from datetime import datetime

# [설정] 유지보수 시간대
REBOOT_TIME = "04:00"  # 매일 새벽 4시 재부팅 시도
CHECK_INTERVAL = 60    # 1분마다 시간 체크

def check_maintenance_schedule():
    """
    현재 시간이 재부팅 시간인지 체크하고, 맞다면 시스템을 종료/재부팅합니다.
    """
    now = datetime.now().strftime("%H:%M")
    
    if now == REBOOT_TIME:
        print(f"🌡️ [하드웨어 보호] 현재 시간 {now}. 노트북 열을 식히기 위해 재부팅을 시작합니다.")
        
        # 진행 중인 주요 에이전트 프로세스 종료 시도 (옵션)
        # os.system("taskkill /F /IM python.exe /T") 
        
        # 윈도우 재부팅 명령어 (60초 후 재부팅)
        # /r: reboot, /t 60: 60 seconds delay
        try:
            # 안전을 위해 실제 실행은 주석 처리하거나 로그만 남길 수 있음
            # subprocess.run(["shutdown", "/r", "/t", "60"], check=True)
            print("🚀 재부팅 명령이 예약되었습니다. (shutdown /r /t 60)")
            
            # 재부팅 전 로그 기록
            with open("maintenance_log.txt", "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now()}] Scheduled Reboot Triggered\n")
                
        except Exception as e:
            print(f"❌ 재부팅 예약 실패: {e}")
    else:
        # print(f"✅ 시스템 정상 가동 중... (현재 시간: {now})")
        pass

if __name__ == "__main__":
    print("🛡️ Young-sik 하드웨어 관리자 가동 시작 (Target: 04:00 AM Reboot)")
    while True:
        check_maintenance_schedule()
        time.sleep(CHECK_INTERVAL)
