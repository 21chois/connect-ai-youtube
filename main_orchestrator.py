"""
main_orchestrator.py — Agent Young-sik 전체 파이프라인
[트렌드 분석] → [영상 생성] → [업로드] → [24h 대기] → [RL 평가]
"""
import os
import sys
import json
import time
import argparse
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# [스토리지 마이그레이션] D드라이브 우선 사용
STORAGE_BASE = os.getenv("STORAGE_BASE_PATH")
if STORAGE_BASE and os.path.exists(os.path.splitdrive(STORAGE_BASE)[0]):
    STORAGE_DIR = Path(STORAGE_BASE)
    log_dir = STORAGE_DIR / "logs"
    OUTPUT_DIR = str(STORAGE_DIR / "output_assets")
else:
    STORAGE_DIR = BASE_DIR
    log_dir = BASE_DIR / "logs"
    OUTPUT_DIR = os.path.join(BASE_DIR, "output_assets")

os.makedirs(log_dir, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

log_path = log_dir / f"youngsik_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_path, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
# Ensure stdout uses utf-8 to avoid CP949 errors on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

log = logging.getLogger("YoungSik")

# ── 로컬 툴 임포트 ────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR / ".agent" / "tools"))

try:
    from trend_analyzer import run_trend_analysis
    from veo_video_maker import generate_long_take
    from image_shorts_maker import create_image_shorts
    from youtube_auto_uploader import (
        get_authenticated_service, upload_video, save_upload_record, post_and_pin_comment
    )
    from evaluate_feedback import auto_evaluate_performance
except ImportError as e:
    log.error(f"Import failed: {e}")
    sys.exit(1)

BANNER = """
+------------------------------------------------------+
|       Agent Young-sik  |  Full YouTube Autopilot     |
|   100% Autonomous YouTube Production System           |
+------------------------------------------------------+
"""

# [메모리 폴더도 이동]
os.makedirs(os.path.join(STORAGE_DIR, ".agent/memory/reward"), exist_ok=True)
os.makedirs(os.path.join(STORAGE_DIR, ".agent/memory/punishment"), exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────
# STEP 1 — Trend Analysis
# ─────────────────────────────────────────────────────────────────────────
def step1_trend_analysis(dry_run: bool = False) -> dict:
    log.info("-" * 60)
    log.info("STEP 1: Starting Commerce Trend Analysis")
    log.info("-" * 60)
    trend = run_trend_analysis(region_code="KR")
    import re
    safe_product = re.sub(r'[^\x00-\x7F가-힣ㄱ-ㅎㅏ-ㅣ\s]', '', trend['product'])
    log.info(f"Target Confirmed: [{safe_product}] | Score: {trend['score']}/100")
    return trend


# ─────────────────────────────────────────────────────────────────────────
# STEP 2 — Video Generation (Veo 3.1 with Image Fallback)
# ─────────────────────────────────────────────────────────────────────────
def step2_generate_video(trend: dict, dry_run: bool = False) -> str:
    log.info("-" * 60)
    log.info("STEP 2: Starting Video Generation")
    log.info("-" * 60)

    product = trend["product"]
    prompts = trend["veo_prompts"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f"video_{timestamp}.mp4")

    # Sample image handling
    sample_img = os.path.join(OUTPUT_DIR, "sample_input.jpg")
    if not os.path.exists(sample_img):
        try:
            from PIL import Image
            img = Image.new("RGB", (1280, 720), color=(240, 240, 245))
            img.save(sample_img, "JPEG")
            log.info(f"   Created default input image: {sample_img}")
        except Exception:
            log.warning("   PIL missing -> please prepare sample_input.jpg manually")
            if dry_run:
                log.info("   [DRY RUN] Skipping video generation")
                return output_path
            return None

    if dry_run:
        log.info(f"   [DRY RUN] Skipping video generation (Path: {output_path})")
        with open(output_path, "wb") as f:
            f.write(b"\x00" * 100)
        return output_path

    log.info(f"   Prompt: {prompts['base_prompt'][:80]}...")
    
    # Try Veo 3.1 First
    try:
        log.info("   Attempting Veo 3.1 Long-take Generation...")
        generate_long_take(
            image_path=sample_img,
            base_prompt=prompts["base_prompt"],
            extend_prompts=prompts["extend_prompts"],
            output_filename=output_path,
        )
        log.info(f"Veo Generation Success: {output_path}")
        return output_path
    except Exception as e:
        log.error(f"Veo Generation Failed: {e}")
        log.warning("   Switching to Fallback: Image-to-Video (MoviePy)...")
        
        try:
            from google import genai
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            
            # Subtitles for fallback (use SEO description or generic ones)
            subtitles = [
                f"Today's Trend: {product}",
                "Analyzing market potential...",
                "This item is going viral!",
                "Check the link in comments for more."
            ]
            
            # Use all prompts for image generation
            all_prompts = [prompts["base_prompt"]] + prompts["extend_prompts"]
            
            success = create_image_shorts(
                client=client,
                prompt=all_prompts,
                output_path=output_path,
                subtitles=subtitles
            )
            
            if success:
                log.info(f"Fallback Generation Success: {output_path}")
                return output_path
            else:
                raise Exception("Fallback creation failed")
                
        except Exception as e2:
            log.error(f"Fallback also failed: {e2}")
            # Final fallback: return dry run file so pipeline doesn't break completely
            with open(output_path, "wb") as f:
                f.write(b"\x00" * 100)
            return output_path


# ─────────────────────────────────────────────────────────────────────────
# STEP 3 — SEO Optimized Upload
# ─────────────────────────────────────────────────────────────────────────
def step3_upload(trend: dict, video_path: str, dry_run: bool = False) -> dict:
    log.info("-" * 60)
    log.info("STEP 3: Starting YouTube SEO Upload")
    log.info("-" * 60)

    seo = trend["seo_metadata"]
    import re
    title_a = re.sub(r'[^\x00-\x7F가-힣ㄱ-ㅎㅏ-ㅣ\s]', '', seo['titles'][0])
    title_b = re.sub(r'[^\x00-\x7F가-힣ㄱ-ㅎㅏ-ㅣ\s]', '', seo['titles'][1])
    log.info(f"   Option A Title: {title_a}")
    log.info(f"   Option B Title: {title_b}")

    youtube_service = get_authenticated_service()

    result = upload_video(
        youtube_service=youtube_service,
        file_path=video_path,
        seo_metadata=seo,
        trend_info=trend,
        privacy_status="private",  # Always upload as private first
        dry_run=dry_run,
    )

    if result:
        save_upload_record(
            video_id=result["id"],
            title=result.get("title", ""),
            veo_prompt=trend["veo_prompts"]["base_prompt"],
            trend_info=trend,
            file_path=video_path,
        )
        log.info(f"Upload record saved: Video ID {result['id']}")

        # [추가] 구매 링크 댓글 작성 및 고정 (준칙 준수: 고지 문구 우선 노출)
        purchase_link = seo.get("purchase_link")
        if purchase_link:
            disclosure = seo.get('disclosure', '')
            comment_text = f"⚠️ {disclosure}\n🛒 최저가 구매 링크: {purchase_link}"
            post_and_pin_comment(youtube_service, result["id"], comment_text)
            log.info("   Pinned comment with purchase link added (Disclosure First).")

    return result


# ─────────────────────────────────────────────────────────────────────────
# STEP 4 — RL Feedback Evaluation
# ─────────────────────────────────────────────────────────────────────────
def step4_evaluate(wait_hours: float = 0, dry_run: bool = False):
    if wait_hours > 0 and not dry_run:
        log.info("-" * 60)
        log.info(f"STEP 4: Waiting {wait_hours} hours for RL Evaluation...")
        log.info("-" * 60)
        time.sleep(wait_hours * 3600)

    log.info("-" * 60)
    log.info("STEP 4: Running RL Self-Feedback Evaluation")
    log.info("-" * 60)
    count = auto_evaluate_performance()
    log.info(f"RL Evaluation Complete: {count} videos processed")


# ─────────────────────────────────────────────────────────────────────────
# Main Execution
# ─────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Agent Young-sik — 100% Autonomous YouTube Pipeline"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Check API only (no actual generation/upload)")
    parser.add_argument("--skip-video", action="store_true",
                        help="Skip video generation (use existing file)")
    parser.add_argument("--skip-upload", action="store_true",
                        help="Skip upload")
    parser.add_argument("--eval-only", action="store_true",
                        help="Run RL evaluation only")
    parser.add_argument("--wait-hours", type=float, default=0,
                        help="Wait time after upload (default: 0 = immediate)")
    args = parser.parse_args()

    print(BANNER)
    start_time = datetime.now()
    log.info(f"Pipeline Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(f"   Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")

    # [추가] API Key 유효성 검사
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        log.error("❌ GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해 주세요.")
        return

    run_report = {
        "started_at": start_time.isoformat(),
        "mode": "dry_run" if args.dry_run else "live",
    }

    try:
        if args.eval_only:
            step4_evaluate(wait_hours=0, dry_run=args.dry_run)
        else:
            # 1. Trend Analysis
            trend = step1_trend_analysis(dry_run=args.dry_run)
            run_report["trend"] = {
                "product": trend["product"],
                "score": trend["score"],
            }

            # 2. Video Generation
            if not args.skip_video:
                video_path = step2_generate_video(trend, dry_run=args.dry_run)
            else:
                # Use latest video file
                mp4_files = list(Path(OUTPUT_DIR).glob("*.mp4"))
                video_path = str(max(mp4_files, key=os.path.getmtime)) if mp4_files else None
                log.info(f"   Skipping video generation -> Using existing: {video_path}")

            run_report["video_path"] = video_path

            # 3. Upload
            upload_result = None
            if not args.skip_upload and video_path:
                upload_result = step3_upload(trend, video_path, dry_run=args.dry_run)
                run_report["upload"] = upload_result

            # 4. RL Evaluation
            step4_evaluate(wait_hours=args.wait_hours, dry_run=args.dry_run)

    except KeyboardInterrupt:
        log.warning("\nUser Interrupted (Ctrl+C)")
    except Exception as e:
        log.error(f"Pipeline Error: {e}", exc_info=True)
    finally:
        elapsed = (datetime.now() - start_time).seconds
        log.info("-" * 60)
        log.info(f"Total Elapsed Time: {elapsed // 60}m {elapsed % 60}s")
        log.info("-" * 60)

        # Save run report
        run_report["finished_at"] = datetime.now().isoformat()
        run_report["elapsed_seconds"] = elapsed
        report_path = f"logs/run_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(run_report, f, indent=2, ensure_ascii=False)
        log.info(f"Run Report: {report_path}")


if __name__ == "__main__":
    main()
