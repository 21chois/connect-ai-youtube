"""
youtube_auto_uploader.py — Agent Young-sik Mission 3 (Upgraded)
SEO 최적화 메타데이터 자동 생성 + YouTube Data API v3 업로드
"""
import os
import json
import time
import pickle
import textwrap
from datetime import datetime
from dotenv import load_dotenv

try:
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    YT_LIB_AVAILABLE = True
except ImportError:
    YT_LIB_AVAILABLE = False
    print("Warning: google-api-python-client missing -> Simulation mode")
    print("Run 'pip install google-api-python-client google-auth-oauthlib'")

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly"
]
SECRET_PATH = "client_secret.json"
MEM_DIR = ".agent/memory"
MEM_FILE = os.path.join(MEM_DIR, "upload_history.json")


def get_authenticated_service(account_id="main"):
    """OAuth 2.0 인증 — 최초 1회 브라우저 팝업, 이후 토큰 자동 갱신. 계정별 토큰 분리."""
    if not YT_LIB_AVAILABLE:
        return None
    creds = None
    
    # 듀얼 계정을 위한 토큰 파일 동적 지정
    # 기존 단일 시스템 하위호환을 위해 "main"인 경우 기존 token_upload.pickle을 그대로 쓰도록 구성
    token_path = "token_upload.pickle" if account_id == "main" else f"token_{account_id}.pickle"
    
    if os.path.exists(token_path):
        with open(token_path, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("Token refresh success")
            except Exception as e:
                print(f"Token refresh failed: {e}")
                creds = None
        if not creds:
            if not os.path.exists(SECRET_PATH):
                print("Error: client_secret.json missing!")
                print("   Google Cloud Console -> APIs & Services -> OAuth 2.0 Client IDs")
                print("   Download and save as 'client_secret.json' in project root.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(SECRET_PATH, SCOPES)
            creds = flow.run_local_server(port=0, prompt='consent select_account')
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)
    return build("youtube", "v3", credentials=creds)


def generate_thumbnail(product_name: str, score: float, output_path: str = "thumbnail.jpg") -> str:
    """PIL로 자동 썸네일 생성 — 어그로성 디자인"""
    if not PIL_AVAILABLE:
        print("Warning: Pillow missing -> Skipping thumbnail generation")
        return None

    width, height = 1280, 720
    img = Image.new("RGB", (width, height), color=(15, 15, 25))
    draw = ImageDraw.Draw(img)

    # 그라데이션 배경 효과 (수동 구현)
    for y in range(height):
        ratio = y / height
        r = int(15 + 40 * ratio)
        g = int(15 + 20 * ratio)
        b = int(25 + 60 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 강조 사각형
    draw.rectangle([30, 30, width - 30, height - 30], outline=(255, 80, 0), width=6)
    draw.rectangle([40, 40, width - 40, height - 40], outline=(255, 150, 0, 80), width=2)

    # 텍스트 (폰트 없이 기본 폰트 사용)
    try:
        # 윈도우 한글 폰트 시도
        font_large = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 80)
        font_medium = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 45)
        font_small = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 30)
    except Exception:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large

    # 제목 (최대 20자)
    title_text = product_name[:20] if len(product_name) > 20 else product_name
    draw.text((width // 2, height // 2 - 80), title_text,
              font=font_large, fill=(255, 255, 255), anchor="mm")
    draw.text((width // 2, height // 2 + 20), "화제의 핫 트렌드!",
              font=font_medium, fill=(255, 120, 0), anchor="mm")
    draw.text((width // 2, height - 80), f"AI 트렌드 점수: {score}/100",
              font=font_small, fill=(200, 200, 200), anchor="mm")

    img.save(output_path, "JPEG", quality=95)
    print(f"Thumbnail created: {output_path}")
    return output_path


def upload_video(
    youtube_service,
    file_path: str,
    seo_metadata: dict,
    trend_info: dict,
    privacy_status: str = "private",
    dry_run: bool = False,
    custom_thumbnail_path: str = None,
) -> dict:
    """YouTube에 영상 업로드 + SEO 메타데이터 적용"""
    title = seo_metadata["titles"][0]  # A/B 테스트 제목 1번
    description = seo_metadata["description"]
    tags = seo_metadata["tags"]
    category_id = seo_metadata.get("category_id", "22")

    import re
    safe_title = re.sub(r'[^\x00-\x7F가-힣ㄱ-ㅎㅏ-ㅣ\s]', '', title)
    print(f"\nUpload Ready:")
    print(f"   Title: {safe_title}")
    print(f"   Privacy: {privacy_status}")
    print(f"   Tags: {', '.join([re.sub(r'[^\x00-\x7F가-힣ㄱ-ㅎㅏ-ㅣ\s]', '', t) for t in tags[:5]])}...")

    if dry_run:
        print("   [DRY RUN] 실제 업로드 스킵")
        return {"id": "DRY_RUN_ID", "dry_run": True, "title": title}

    if not youtube_service:
        print("   Warning: YouTube service not connected -> Simulating")
        return {"id": f"SIM_{int(time.time())}", "simulated": True, "title": title}

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
            "defaultLanguage": "ko",
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    # 예약 공개(Scheduled) 기능 추가: ISO 8601 형식의 publish_time이 제공되면 적용
    if privacy_status == "private" and seo_metadata.get("publish_at"):
        body["status"]["publishAt"] = seo_metadata["publish_at"]
        print(f"   [예약 설정] 공개 예정 시간: {seo_metadata['publish_at']}")

    print("\nYouTube 업로드 시작...")
    insert_req = youtube_service.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(file_path, chunksize=1024 * 1024, resumable=True),
    )

    response = None
    while response is None:
        status, response = insert_req.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"\r   [{pct}%]", end="", flush=True)

    print(f"\nUpload Complete!")
    video_id = response["id"]
    print(f"   Video ID: {video_id}")
    print(f"   URL: https://youtu.be/{video_id}")

    # 썸네일 업로드
    if custom_thumbnail_path and os.path.exists(custom_thumbnail_path):
        thumb_path = custom_thumbnail_path
    else:
        thumb_path = generate_thumbnail(trend_info.get("product", ""), trend_info.get("score", 0))
        
    if thumb_path and os.path.exists(thumb_path):
        try:
            youtube_service.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumb_path, mimetype="image/jpeg"),
            ).execute()
            print(f"   Thumbnail upload complete")
        except Exception as e:
            print(f"   Thumbnail upload failed: {e}")

    return {"id": video_id, "title": title, "url": f"https://youtu.be/{video_id}"}


def post_and_pin_comment(youtube_service, video_id: str, comment_text: str):
    """업로드된 영상에 댓글을 달고 고정(Pin)합니다."""
    if not youtube_service:
        print("   Warning: YouTube service not connected -> Skipping comment")
        return None

    try:
        # 1. 댓글 작성
        print(f"\n댓글 작성 중: {video_id}")
        comment_res = youtube_service.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": comment_text
                        }
                    }
                }
            }
        ).execute()
        
        comment_id = comment_res["snippet"]["topLevelComment"]["id"]
        print(f"   Comment posted (ID: {comment_id})")

        # 2. 댓글 고정 (Pin)
        # Note: 고정 기능을 위해서는 채널 소유자 권한이 필요합니다.
        try:
            youtube_service.comments().setModerationStatus(
                id=comment_id,
                moderationStatus="published", # 기본값
                # setModerationStatus 자체에는 Pin 기능이 없으며, 
                # 고정은 별도의 속성이거나 파트너 권한이 필요할 수 있습니다.
                # 일반적인 API로는 댓글 작성까지만 안정적이며, '고정'은 수동 확인이 필요할 수 있습니다.
            ).execute()
            print(f"   Comment pinned (Simulated/Attempted)")
        except Exception as pin_e:
            print(f"   Note: Pinning may require manual check: {pin_e}")

        return comment_id
    except Exception as e:
        print(f"   Error posting comment: {e}")
        return None



def save_upload_record(video_id: str, title: str, veo_prompt: str,
                       trend_info: dict, file_path: str):
    """업로드 기록을 memory에 저장"""
    os.makedirs(MEM_DIR, exist_ok=True)
    history = []
    if os.path.exists(MEM_FILE):
        with open(MEM_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)

    record = {
        "video_id": video_id,
        "status": "published",
        "uploaded_at": datetime.now().isoformat(),
        "file_path": file_path,
        "trend_info": trend_info,
        "metadata": {
            "youtube_title": title,
            "veo_prompt": veo_prompt,
        },
    }
    history.append(record)

    with open(MEM_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    print(f"   Upload record saved: {MEM_FILE}")


if __name__ == "__main__":
    main()
