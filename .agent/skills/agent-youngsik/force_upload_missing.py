import os
import sys
import json
import time
from datetime import datetime

# [설정] 프로젝트 루트 및 도구 폴더 경로 확보
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SKILL_DIR, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agent", "tools"))

from youtube_auto_uploader import get_authenticated_service, upload_video, save_upload_record

def force_upload():
    print("🚀 [긴급 복구] 10일 이후 누락 영상 일괄 업로드 프로세스 시작")
    os.chdir(ROOT_DIR)

    # 복구 대상 리스트 (메인/서브 채널 분리)
    targets = [
        # --- 메인 채널 [sung AA] ---
        {
            "file": "output_assets/dubai_series_ep1_20260509_120012.mp4",
            "account": "main",
            "title": "📺 이거 구하려고 편의점 10군데 돌았습니다... 두바이 초콜릿 언박싱! (EP.1)",
            "tags": ["두바이초콜릿", "편의점신상", "언박싱", "먹방", "쇼츠"],
            "desc": "화제의 두바이 초콜릿, 드디어 구했습니다! 실물 영접 리뷰.\n\n#두바이초콜릿 #신상리뷰 #쇼츠"
        },
        {
            "file": "output_assets/dubai_series_ep2_20260510_085210.mp4",
            "account": "main",
            "title": "🤯 두바이 초콜릿에 숨겨진 충격적인 진실 3가지 l #쇼츠 #알쓸신잡 (EP.2)",
            "tags": ["두바이초콜릿", "상식", "알쓸신잡", "꿀팁", "쇼츠"],
            "desc": "당신이 몰랐던 두바이 초콜릿의 비밀.\n\n#두바이초콜릿 #비밀 #쇼츠"
        },
        {
            "file": "output_assets/dubai_series_ep3_20260510_121547.mp4",
            "account": "main",
            "title": "🆚 원조 두바이 초콜릿 vs 편의점 신상 블라인드 테스트 결과는?! (EP.3)",
            "tags": ["두바이초콜릿", "비교리뷰", "블라인드테스트", "먹방", "쇼츠"],
            "desc": "어느 쪽이 더 맛있을까요? 반전 결과 확인하세요.\n\n#두바이초콜릿 #비교 #쇼츠"
        },
        {
            "file": "output_assets/dubai_series_ep4_20260510_125208.mp4",
            "account": "main",
            "title": "🧑‍🍳 단돈 1만원으로 두바이 초콜릿 100% 똑같이 만드는 레시피 폭로 (EP.4)",
            "tags": ["두바이초콜릿레시피", "홈메이드", "요리", "꿀팁", "쇼츠"],
            "desc": "집에서도 만들 수 있습니다. 황금 레시피 공개!\n\n#두바이초콜릿 #레시피 #요리쇼츠"
        },
        {
            "file": "output_assets/dubai_series_ep5_20260510_161605.mp4",
            "account": "main",
            "title": "🍩 드디어 선넘은 두바이 초콜릿... 수제 공방 두바이 도넛 리얼 리뷰 (EP.5)",
            "tags": ["두바이초콜릿", "두바이도넛", "디저트", "먹방", "쇼츠"],
            "desc": "이제는 도넛까지? 두바이 초콜릿의 진화.\n\n#두바이초콜릿 #디저트 #쇼츠"
        },
        # --- 서브 채널 [AI 스마트팜 TV] ---
        {
            "file": "output_assets/lotto_jeju_olle_20260512_231958.mp4",
            "account": "sub",
            "title": "🔮 [제주 스페셜] 서귀포 올레시장에서 만난 링도사! 성실한 어머님께 점지한 로또 번호는?",
            "tags": ["로또", "제주도", "올레시장", "링도사", "행운", "쇼츠"],
            "desc": "📍 제주 서귀포 올레시장 스페셜!\n성실한 어머님께 전하는 링도사의 행운 번호.\n\n#로또 #제주도 #링도사 #행운"
        },
        {
            "file": "output_assets/kaimak_special_20260511_213221.mp4",
            "account": "sub",
            "title": "🥛 백종원이 '천상의 맛'이라 극찬한 이유... 진짜 카이막 먹방 l #카이막 #리뷰",
            "tags": ["카이막", "백종원", "천상의맛", "디저트", "먹방", "쇼츠"],
            "desc": "이건 진짜 사기입니다. 천상의 맛 카이막 리얼 리뷰.\n\n#카이막 #백종원 #천상의맛 #먹방"
        }
    ]

    for t in targets:
        full_path = os.path.join(ROOT_DIR, t["file"])
        if not os.path.exists(full_path):
            print(f"⚠️ 파일을 찾을 수 없음: {full_path}")
            continue

        print(f"\n📤 [{t['account'].upper()}] 업로드 중: {t['file']}")
        youtube_service = get_authenticated_service(account_id=t["account"])
        
        if not youtube_service:
            print(f"❌ {t['account']} 계정 인증 실패")
            continue

        seo_metadata = {
            "titles": [t["title"]],
            "description": t["desc"],
            "tags": t["tags"],
            "category_id": "22"
        }
        
        try:
            result = upload_video(
                youtube_service=youtube_service,
                file_path=full_path,
                seo_metadata=seo_metadata,
                trend_info={"product": "recovery"},
                privacy_status="public" # 전체 공개 설정
            )
            
            if result:
                save_upload_record(
                    video_id=result["id"],
                    title=result.get("title", ""),
                    veo_prompt=f"Recovery Upload: {t['file']}",
                    trend_info={"product": "recovery"},
                    file_path=full_path
                )
                print(f"✅ 업로드 성공: {result.get('url')}")
                # 쿼터 보호를 위한 짧은 대기
                time.sleep(5)
        except Exception as e:
            print(f"❌ {t['file']} 업로드 실패: {e}")

if __name__ == "__main__":
    force_upload()
