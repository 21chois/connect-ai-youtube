"""
evaluate_feedback.py — Agent Young-sik Mission 4 (Upgraded)
YouTube Analytics API로 실제 메트릭 수집 → RL reward/punishment 판정
"""
import os
import json
import pickle
from datetime import datetime, timedelta
from dotenv import load_dotenv

import sys
import io

# YouTube Analytics API
try:
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False
    print("Warning: google-api-python-client missing -> Simulation mode")

load_dotenv()

# Ensure stdout uses utf-8 to avoid CP949 errors on Windows
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MEM_DIR = ".agent/memory"
MEM_FILE = os.path.join(MEM_DIR, "upload_history.json")
REWARD_DIR = os.path.join(MEM_DIR, "reward")
PUNISH_DIR = os.path.join(MEM_DIR, "punishment")

# RL 임계값 설정
THRESHOLDS = {
    "views": 10000,       # 조회수 1만 이상
    "ctr": 5.0,           # CTR 5% 이상
    "avd_ratio": 0.4,     # 평균 시청률 40% 이상
    "likes": 200,         # 좋아요 200개 이상
}

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


def get_analytics_service():
    """YouTube Analytics API OAuth 인증"""
    if not ANALYTICS_AVAILABLE:
        return None
    creds = None
    token_path = "token_analytics.pickle"
    if os.path.exists(token_path):
        with open(token_path, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif os.path.exists("client_secret.json"):
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
            with open(token_path, "wb") as f:
                pickle.dump(creds, f)
        else:
            print("Warning: client_secret.json missing -> Simulation mode")
            return None
    return build("youtubeAnalytics", "v2", credentials=creds)


def fetch_video_metrics(analytics_service, video_id: str) -> dict:
    """YouTube Analytics API로 영상 성과 지표 수집"""
    if not analytics_service:
        # 시뮬레이션 모드
        import random
        return {
            "views": random.randint(500, 50000),
            "ctr": round(random.uniform(1.0, 12.0), 2),
            "avd_ratio": round(random.uniform(0.15, 0.75), 2),
            "likes": random.randint(10, 2000),
            "comments": random.randint(2, 300),
            "mode": "simulation",
        }
    try:
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        response = analytics_service.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="views,likes,comments,averageViewDuration,averageViewPercentage",
            filters=f"video=={video_id}",
        ).execute()
        rows = response.get("rows", [[0, 0, 0, 0, 0]])
        row = rows[0] if rows else [0, 0, 0, 0, 0]
        return {
            "views": int(row[0]),
            "likes": int(row[1]),
            "comments": int(row[2]),
            "avd_seconds": float(row[3]),
            "avd_ratio": float(row[4]) / 100,
            "ctr": 0.0,  # CTR은 별도 Search Console 데이터 필요
            "mode": "live",
        }
    except Exception as e:
        print(f"Warning: Analytics API error: {e} -> Simulation mode")
        import random
        return {
            "views": random.randint(500, 50000),
            "ctr": round(random.uniform(1.0, 12.0), 2),
            "avd_ratio": round(random.uniform(0.15, 0.75), 2),
            "likes": random.randint(10, 2000),
            "mode": "simulation_fallback",
        }


def compute_rl_verdict(metrics: dict) -> dict:
    """강화학습 판정 로직 — reward or punishment"""
    scores = {
        "views": metrics.get("views", 0) >= THRESHOLDS["views"],
        "ctr": metrics.get("ctr", 0) >= THRESHOLDS["ctr"],
        "avd_ratio": metrics.get("avd_ratio", 0) >= THRESHOLDS["avd_ratio"],
        "likes": metrics.get("likes", 0) >= THRESHOLDS["likes"],
    }
    passed = sum(scores.values())
    total = len(scores)
    is_reward = passed >= 2  # 4개 중 2개 이상 통과 시 reward

    verdict = {
        "result": "reward" if is_reward else "punishment",
        "passed_criteria": passed,
        "total_criteria": total,
        "score_breakdown": scores,
        "reward_rate": f"{passed}/{total}",
    }
    return verdict


def write_odam_note(video_id: str, title: str, metrics: dict, verdict: dict,
                    veo_prompt: str, trend_info: dict):
    """오답노트(오답: punishment, 정답: reward) 마크다운 생성"""
    os.makedirs(REWARD_DIR, exist_ok=True)
    os.makedirs(PUNISH_DIR, exist_ok=True)

    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    result = verdict["result"]
    target_dir = REWARD_DIR if result == "reward" else PUNISH_DIR
    filename = os.path.join(target_dir, f"{now_str}_{video_id[:8]}.md")

    header = f"# {'Success Analysis' if result == 'reward' else 'Failure Analysis'} - {now_str}\n\n"

    content = header + f"""## 영상 정보
- **Video ID:** `{video_id}`
- **제목:** {title}
- **평가일:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 성과 지표
| 지표 | 측정값 | 임계값 | 통과 |
|------|--------|--------|------|
| 조회수 | {metrics.get('views', 0):,} | {THRESHOLDS['views']:,} | {'✅' if verdict['score_breakdown']['views'] else '❌'} |
| CTR | {metrics.get('ctr', 0):.1f}% | {THRESHOLDS['ctr']}% | {'✅' if verdict['score_breakdown']['ctr'] else '❌'} |
| 평균 시청률 | {metrics.get('avd_ratio', 0)*100:.1f}% | {THRESHOLDS['avd_ratio']*100}% | {'✅' if verdict['score_breakdown']['avd_ratio'] else '❌'} |
| 좋아요 | {metrics.get('likes', 0):,} | {THRESHOLDS['likes']:,} | {'✅' if verdict['score_breakdown']['likes'] else '❌'} |

**판정:** `{result.upper()}` ({verdict['reward_rate']} 기준 통과)

## 사용된 Veo 프롬프트
```
{veo_prompt}
```

## 트렌드 분석 정보
- **선정 제품:** {trend_info.get('product', 'N/A')}
- **커머스 점수:** {trend_info.get('score', 'N/A')}/100
- **선정 이유:** {trend_info.get('trend_reason', 'N/A')}

{"- Next Step: Keep this pattern" if result == 'reward' else "- Improvement: Need closer shots"}
{"- Trend Strategy Valid" if result == 'reward' else "- Keyword Density Increase Required"}
{"- SEO Structure Maintain" if result == 'reward' else "- Title Hook Strength Increase Required"}
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"   Feedback note saved: {filename}")
    return filename


def auto_evaluate_performance():
    """전체 RL 평가 파이프라인 실행"""
    print("=" * 60)
    print("[Agent Young-sik] Mission 4: Self-Feedback (RL)")
    print(f"Evaluation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    if not os.path.exists(MEM_FILE):
        print("Warning: No upload history. Run main_orchestrator.py first.")
        return

    with open(MEM_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)

    analytics = get_analytics_service()
    evaluated_count = 0

    for i, record in enumerate(history):
        if record.get("status") == "published":
            video_id = record.get("video_id", "unknown")
            meta = record.get("metadata", {})
            title = meta.get("youtube_title", "제목 없음")
            veo_prompt = meta.get("veo_prompt", "")
            trend_info = record.get("trend_info", {})

            # Strip emojis from title for console printing
            import re
            clean_title = re.sub(r'[^\x00-\x7F가-힣ㄱ-ㅎㅏ-ㅣ\s]', '', title)
            print(f"\n[{i+1}] Evaluating video: {clean_title[:40]}...")

            # 메트릭 수집
            metrics = fetch_video_metrics(analytics, video_id)
            print(f"   Views: {metrics.get('views', 0):,} | CTR: {metrics.get('ctr', 0):.1f}%")

            # RL 판정
            verdict = compute_rl_verdict(metrics)
            print(f"   Verdict: {verdict['result'].upper()} ({verdict['reward_rate']} passed)")

            # 오답노트 작성
            note_path = write_odam_note(video_id, title, metrics, verdict, veo_prompt, trend_info)

            # 히스토리 업데이트
            history[i]["status"] = "evaluated"
            history[i]["evaluation"] = {
                "metrics": metrics,
                "verdict": verdict,
                "note_path": note_path,
                "evaluated_at": datetime.now().isoformat(),
            }
            evaluated_count += 1

    with open(MEM_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    print(f"\nEvaluation Complete: {evaluated_count} videos processed")
    return evaluated_count


if __name__ == "__main__":
    auto_evaluate_performance()
