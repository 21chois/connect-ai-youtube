import os
import sys
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime

# [설정] 프로젝트 루트 및 도구 폴더 경로 확보
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, ".agent", "tools"))

def check_token(account_id):
    token_path = os.path.join(BASE_DIR, "token_upload.pickle" if account_id == "main" else f"token_{account_id}.pickle")
    if not os.path.exists(token_path):
        print(f"❌ {account_id}: 토큰 파일 없음 ({token_path})")
        return None
    
    try:
        with open(token_path, "rb") as f:
            creds = pickle.load(f)
        
        service = build("youtube", "v3", credentials=creds)
        channels = service.channels().list(part="snippet,contentDetails", mine=True).execute()
        
        if "items" in channels:
            channel = channels["items"][0]
            title = channel["snippet"]["title"]
            channel_id = channel["id"]
            print(f"✅ {account_id}: 연동됨 -> 채널명: [{title}] (ID: {channel_id})")
            
            # 최신 영상 1개 확인
            videos = service.search().list(part="snippet", forMine=True, type="video", maxResults=1, order="date").execute()
            if "items" in videos:
                v = videos["items"][0]
                print(f"   ㄴ 최신 영상: {v['snippet']['title']} (ID: {v['id']['videoId']}, 시간: {v['snippet']['publishedAt']})")
            else:
                print("   ㄴ 최신 영상 없음")
            return channel_id
        else:
            print(f"❌ {account_id}: 채널 정보를 가져올 수 없음")
    except Exception as e:
        print(f"❌ {account_id}: 에러 발생 - {e}")
    return None

if __name__ == "__main__":
    print(f"--- YouTube API 진단 보고서 ({datetime.now()}) ---")
    main_id = check_token("main")
    sub_id = check_token("sub")
    
    if main_id and sub_id and main_id == sub_id:
        print("\n⚠️ 경고: 'main'과 'sub' 계정이 동일한 채널로 설정되어 있습니다.")
    elif main_id and sub_id:
        print("\n✨ 'main'과 'sub' 계정이 서로 다른 채널로 정상 분리되어 있습니다.")
