import os
import shutil
from datetime import datetime

def cleanup():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "output_assets")
    archive_dir = os.path.join(base_dir, "archive", "20260510_backup")
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🧹 시스템 정밀 클린업 시작...")
    
    # 아카이브 폴더 생성
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        print(f" ✅ 아카이브 폴더 생성 완료: {archive_dir}")
    
    # 5월 10일 이후 에셋 리스트 (파일명 기준 필터링)
    target_date = "20260510"
    moved_count = 0
    
    if os.path.exists(assets_dir):
        for filename in os.listdir(assets_dir):
            # 파일명에 날짜가 포함된 경우 체크 (예: lotto_jeju_olle_20260510_...)
            if any(date in filename for date in ["20260510", "20260511", "20260512", "20260513"]):
                src = os.path.join(assets_dir, filename)
                dst = os.path.join(archive_dir, filename)
                try:
                    shutil.move(src, dst)
                    moved_count += 1
                except Exception as e:
                    print(f" ⚠️ 이동 실패 ({filename}): {e}")
    
    # 루트 디렉토리의 임시 파일 및 로그 정리
    for filename in os.listdir(base_dir):
        if filename.startswith("temp_audio") or filename.endswith("TEMP_MPY_wvf_snd.mp4") or filename == "thumbnail.jpg":
            try:
                os.remove(os.path.join(base_dir, filename))
                print(f" 🗑️ 임시 파일 삭제: {filename}")
            except:
                pass

    print(f"\n✨ 클린업 완료! 총 {moved_count}개의 에셋을 아카이브로 이동했습니다.")
    print("이제 시스템이 5월 9일 이전의 안정적인 상태로 준비되었습니다.")

if __name__ == "__main__":
    cleanup()
