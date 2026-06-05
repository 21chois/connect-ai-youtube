import os
import json
import sys

# agent/tools 폴더 모듈 로드
sys.path.append(os.path.join(os.path.dirname(__file__), ".agent", "tools"))
from youtube_auto_uploader import get_authenticated_service, upload_video, post_and_pin_comment

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "hybrid_commerce_config.json")

def main():
    # 유튜브 인증 모듈이 상대 경로("client_secret.json")를 사용하므로 작업 폴더를 강제로 맞춥니다.
    os.chdir(BASE_DIR)
    
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    item = config["items"][1] # 몬스터 클리어 겔 테이프
    
    # 아까 렌더링 된 파일 이름
    file_name = "hybrid_item_02_1779007107.mp4"
    file_path = os.path.join(r"D:\유튜브_데이터_영식\output_assets", file_name)
    if not os.path.exists(file_path):
        file_path = os.path.join(BASE_DIR, "output_assets", file_name)
        
    if not os.path.exists(file_path):
        print(f"오류: 영상을 찾을 수 없습니다 -> {file_path}")
        return

    print(f"🎬 업로드 준비 중: {file_path}")
    
    youtube = get_authenticated_service("main")
    if not youtube:
        print("유튜브 인증 실패")
        return
        
    # SEO 및 설명란 세팅
    desc_text = item["comment_template"].format(affiliate_url=item["affiliate_url"])
    seo = {
        "titles": [item["youtube_title"]],
        "description": f"무조건 사야 하는 자취생 필수템 정리!\n\n{desc_text}",
        "tags": item["youtube_tags"],
        "category_id": "22" 
    }
    
    # 🚨 댓글 막힘 방지를 위해 무조건 '일부 공개(unlisted)'로 먼저 업로드
    print("🚀 유튜브 서버로 전송 중...")
    res = upload_video(youtube, file_path, seo, trend_info={"product": item["name"], "score": 99}, privacy_status="unlisted")
    
    video_id = res["id"]
    
    # 자동 댓글 작성
    print("📝 수익화 고정 댓글 작성 중...")
    post_and_pin_comment(youtube, video_id, desc_text)
    
    print("\n✅ 업로드 및 댓글 세팅이 완벽하게 끝났습니다!")
    print(f"👉 스튜디오 확인 링크: https://studio.youtube.com/video/{video_id}/edit")
    print("👉 스튜디오에 들어가셔서 댓글창이 열려있는지 확인 후, [공개]로만 바꿔주시면 바로 수익 창출 시작입니다!")

if __name__ == "__main__":
    main()
