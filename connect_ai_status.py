import os
import json
import glob
from datetime import datetime

def get_system_status():
    print("=" * 60)
    print("      🏢 Connect AI (AI 1인 기업) 시스템 상태 보고서")
    print("=" * 60)
    
    # 1. 환경 변수 체크
    print("\n[1] 환경 변수 설정 상태")
    env_vars = ["GEMINI_API_KEY", "YOUTUBE_DATA_API_KEY"]
    for var in env_vars:
        status = "✅ 설정됨" if os.getenv(var) else "❌ 미설정"
        print(f" - {var}: {status}")
        
    # 2. 최근 업로드 내역
    print("\n[2] 최근 유튜브 업로드 내역 (Last 3)")
    upload_history_path = ".agent/memory/upload_history.json"
    if os.path.exists(upload_history_path):
        with open(upload_history_path, "r", encoding="utf-8") as f:
            history = json.load(f)
            # history is likely a list or dict. Let's handle list.
            if isinstance(history, list):
                for item in history[-3:]:
                    print(f" - [{item.get('timestamp', 'N/A')}] {item.get('title', 'Unknown Title')} (ID: {item.get('video_id')})")
            elif isinstance(history, dict):
                # handle dict if history is keyed by video_id
                items = list(history.values())
                for item in items[-3:]:
                    print(f" - {item.get('title', 'Unknown Title')} (ID: {item.get('video_id')})")
    else:
        print(" - 내역 없음")
        
    # 3. 최근 트렌드 분석 결과
    print("\n[3] 최근 발굴된 트렌드 아이템 (Last 3)")
    trend_history_path = ".agent/memory/trend_history.json"
    if os.path.exists(trend_history_path):
        with open(trend_history_path, "r", encoding="utf-8") as f:
            trends = json.load(f)
            if isinstance(trends, list):
                for t in trends[-3:]:
                    print(f" - {t.get('product', 'Unknown')} (Score: {t.get('score', 'N/A')})")
    else:
        print(" - 내역 없음")
        
    # 4. 최근 시스템 로그
    print("\n[4] 최근 시스템 로그 (youngsik_*.log)")
    log_files = glob.glob("logs/youngsik_*.log")
    if log_files:
        latest_log = max(log_files, key=os.path.getmtime)
        print(f" - 최신 로그 파일: {os.path.basename(latest_log)}")
        with open(latest_log, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[-3:]:
                print(f"   > {line.strip()}")
    else:
        print(" - 로그 파일 없음")

    print("\n" + "=" * 60)
    print(f"보고서 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    get_system_status()
