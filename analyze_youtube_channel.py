import os
import sys
import pickle
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, "token_upload.pickle")

def analyze_channel():
    if not os.path.exists(TOKEN_PATH):
        print("토큰 파일(token_upload.pickle)이 없습니다.")
        return

    try:
        with open(TOKEN_PATH, "rb") as f:
            creds = pickle.load(f)
        
        service = build("youtube", "v3", credentials=creds)
        
        # 1. 채널 정보 가져오기
        channels_response = service.channels().list(
            part="snippet,statistics,contentDetails",
            mine=True
        ).execute()
        
        if not channels_response["items"]:
            print("채널 정보를 찾을 수 없습니다.")
            return
            
        channel = channels_response["items"][0]
        title = channel["snippet"]["title"]
        stats = channel["statistics"]
        uploads_playlist_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
        
        print(f"=== 채널 분석 보고서: {title} ===")
        print(f"구독자 수: {stats.get('subscriberCount', '0')}")
        print(f"총 조회수: {stats.get('viewCount', '0')}")
        print(f"총 영상 수: {stats.get('videoCount', '0')}\n")
        
        # 2. 최근 업로드된 영상 5개 가져오기
        playlist_items_response = service.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=5
        ).execute()
        
        video_ids = [item["snippet"]["resourceId"]["videoId"] for item in playlist_items_response["items"]]
        
        if not video_ids:
            print("최근 업로드된 영상이 없습니다.")
            return
            
        # 3. 영상별 상세 통계 가져오기
        videos_response = service.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids)
        ).execute()
        
        print("=== 최근 업로드 영상(Top 5) 성과 분석 ===")
        for video in videos_response["items"]:
            v_title = video["snippet"]["title"]
            v_stats = video["statistics"]
            v_views = v_stats.get("viewCount", "0")
            v_likes = v_stats.get("likeCount", "0")
            v_comments = v_stats.get("commentCount", "0")
            v_published = video["snippet"]["publishedAt"]
            
            print(f"- 제목: {v_title}")
            print(f"  업로드일: {v_published[:10]}")
            print(f"  조회수: {v_views} | 좋아요: {v_likes} | 댓글: {v_comments}\n")

    except Exception as e:
        print(f"분석 중 오류 발생: {e}")

if __name__ == "__main__":
    analyze_channel()
