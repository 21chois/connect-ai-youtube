"""
trend_analyzer.py — Agent Young-sik Mission 1
구글 트렌드 + YouTube 급상승 분석 → 커머스 가능한 실존 제품 타겟팅
"""
import os
import json
import time
import random
from datetime import datetime
from dotenv import load_dotenv
import requests

import sys
import io

load_dotenv()

# Ensure stdout uses utf-8 to avoid CP949 errors on Windows
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

YT_API_KEY = os.getenv("YOUTUBE_DATA_API_KEY")

# 허구/혐오 필터링 블랙리스트
BLACKLIST = [
    "imaginary", "fictional", "fake", "gross", "disgusting", "bizarre",
    "혐오", "기괴", "허구", "가짜", "상상", "괴물", "역겨",
]

# 커머스 가능 카테고리 (실존 제품군)
COMMERCE_CATEGORIES = [
    "food", "snack", "drink", "gadget", "beauty", "skincare",
    "fashion", "health", "kitchen", "tech", "fitness",
    "음식", "간식", "음료", "가젯", "뷰티", "패션", "건강", "주방",
]

TRENDING_KEYWORDS_KR = [
    "신제품", "요즘 뜨는", "맛집", "신상", "핫템", "역대급", "강추",
    "가성비", "인기폭발", "품절대란", "먹방", "리뷰", "언박싱",
]


def fetch_youtube_trending(region_code="KR", max_results=10):
    """YouTube Data API v3로 급상승 동영상 키워드 수집"""
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region_code,
        "maxResults": max_results,
        "videoCategoryId": "1",  # Film & Entertainment → 넓게 수집
        "key": YT_API_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        results = []
        for item in data.get("items", []):
            snippet = item["snippet"]
            stats = item.get("statistics", {})
            title = snippet.get("title", "")
            tags = snippet.get("tags", [])
            views = int(stats.get("viewCount", 0))
            results.append({
                "title": title,
                "tags": tags[:10],
                "views": views,
                "channel": snippet.get("channelTitle", ""),
                "published": snippet.get("publishedAt", ""),
            })
        return sorted(results, key=lambda x: x["views"], reverse=True)
    except Exception as e:
        print(f"Warning: YouTube Trending fetch failed: {e}")
        return []


def fetch_google_trends_fallback():
    """pytrends 없이 구글 트렌드 RSS로 한국 실시간 급상승 수집"""
    url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=KR"
    try:
        r = requests.get(url, timeout=10,
                         headers={"User-Agent": "Mozilla/5.0"})
        # 간단 파싱 (XML → title 추출)
        titles = []
        for line in r.text.split("\n"):
            line = line.strip()
            if line.startswith("<title>") and "Google Trends" not in line:
                title = line.replace("<title>", "").replace("</title>", "").strip()
                if title:
                    titles.append(title)
        return titles[:20]
    except Exception as e:
        print(f"Warning: Google Trends RSS fetch failed: {e}")
        return []


def is_blacklisted(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in BLACKLIST)


def score_commerce_potential(title: str, tags: list, views: int) -> float:
    """커머스 잠재력 점수 산출 (0~100)"""
    score = 0.0
    combined = (title + " " + " ".join(tags)).lower()

    # 블랙리스트 필터
    if is_blacklisted(combined):
        return 0.0

    # 조회수 기반 기본 점수 (최대 40점)
    score += min(views / 500000 * 40, 40)

    # 커머스 카테고리 매칭 (최대 30점)
    cat_matches = sum(1 for c in COMMERCE_CATEGORIES if c in combined)
    score += min(cat_matches * 10, 30)

    # 한국 트렌드 키워드 매칭 (최대 30점)
    kw_matches = sum(1 for kw in TRENDING_KEYWORDS_KR if kw in combined)
    score += min(kw_matches * 10, 30)

    return round(min(score, 100), 1)


def generate_veo_prompt(product_name: str, trend_reason: str) -> dict:
    """Veo 3.1용 cinematic 프롬프트 자동 생성"""
    base = (
        f"Cinematic 16:9 advertisement shot of '{product_name}'. "
        f"Ultra-HD, warm studio lighting, shallow depth of field. "
        f"The product is presented on a clean white marble surface. "
        f"Slow dolly-in movement reveals premium packaging details. "
        f"Photo-realistic, 8K quality."
    )
    extend = [
        f"The camera orbits around the '{product_name}', revealing all angles. "
        f"Steam or condensation adds life to the scene. Cinematic color grading.",
        f"Close-up macro shot of '{product_name}' texture and details. "
        f"Soft bokeh background. Professional food/product photography style.",
        f"Hero angle wide shot: '{product_name}' surrounded by complementary props. "
        f"Golden hour lighting. Lifestyle commercial atmosphere.",
    ]
    return {"base_prompt": base, "extend_prompts": extend}


def generate_seo_metadata(product_name: str, score: float, trend_reason: str) -> dict:
    """어그로성 SEO 메타데이터 자동 생성 및 구매 링크 포함"""
    # [수정] 쿠팡 파트너스 채널 ID 반영
    sub_id = os.getenv("COUPANG_SUB_ID", "AISetup365")
    search_query = product_name.replace(" ", "+")
    purchase_link = f"https://www.coupang.com/np/search?q={search_query}&subId={sub_id}"
    disclosure = "이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."

    titles = [
        f"🔥 {product_name} 품절대란?! 지금 당장 사야 하는 이유 | 솔직 리뷰",
        f"충격) {product_name} 직접 써봤더니... 이게 진짜야?! [내돈내산]",
    ]
    description = (
        f"⚠️ {disclosure}\n\n"
        f"📦 {product_name} 완전 정복!\n\n"
        f"🏆 트렌드 점수: {score}/100 | 분석일: {datetime.now().strftime('%Y.%m.%d')}\n\n"
        f"📊 선정 이유: {trend_reason}\n\n"
        f"🛒 최저가 확인 및 구매하기: {purchase_link}\n\n"
        f"🤖 이 영상은 AI 에이전트 영식(Young-sik)이 자동 제작했습니다.\n\n"
        f"#{''.join(product_name.split())} #신상리뷰 #핫템 #강추 #내돈내산 #먹방 #언박싱\n\n"
        f"📌 타임라인:\n0:00 오프닝\n0:05 제품 소개\n0:15 실사용 장면\n"
    )
    tags = [
        product_name, "신상", "핫템", "강추", "내돈내산", "품절대란",
        "리뷰", "언박싱", "가성비", "먹방", "2026신상", "트렌드",
        "쇼핑", "추천", "유용한제품"
    ]
    return {
        "titles": titles,
        "description": description,
        "tags": tags[:15],
        "category_id": "22",  # People & Blogs
        "purchase_link": purchase_link,
        "disclosure": disclosure
    }


def run_trend_analysis(region_code="KR") -> dict:
    """전체 트렌드 분석 실행 → 최적 타겟 반환"""
    print("=" * 60)
    print("[Agent Young-sik] Mission 1: Commerce Trend Analysis")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. YouTube Trending
    print("\nFetching YouTube Trending videos...")
    yt_trends = fetch_youtube_trending(region_code=region_code, max_results=15)
    print(f"   -> {len(yt_trends)} videos collected")

    # 2. Google Trends
    print("\nFetching Google Trends keywords...")
    g_trends = fetch_google_trends_fallback()
    print(f"   -> {len(g_trends)} keywords collected")

    # 3. 점수 산출
    candidates = []
    for item in yt_trends:
        score = score_commerce_potential(item["title"], item["tags"], item["views"])
        if score > 0:
            candidates.append({
                "product": item["title"][:50],
                "score": score,
                "views": item["views"],
                "tags": item["tags"][:5],
                "source": "youtube_trending",
                "trend_reason": f"YouTube 급상승 조회수 {item['views']:,}회",
            })

    # Google 트렌드 키워드 추가
    for kw in g_trends[:5]:
        if not is_blacklisted(kw):
            score = score_commerce_potential(kw, [], 100000)
            if score > 0:
                candidates.append({
                    "product": kw,
                    "score": score,
                    "views": 0,
                    "tags": [],
                    "source": "google_trends",
                    "trend_reason": f"Google 실시간 급상승 키워드: {kw}",
                })

    if not candidates:
        # 폴백: 기본 인기 카테고리
        fallback_products = ["편의점 신상 삼각김밥", "제로 콜라 신제품", "갤럭시 링"]
        candidates = [{
            "product": p,
            "score": random.uniform(60, 85),
            "views": 0,
            "tags": ["신상", "리뷰"],
            "source": "fallback",
            "trend_reason": "API 데이터 부족 → 기본 인기 카테고리 적용",
        } for p in fallback_products]

    # 4. 최고 점수 타겟 선택
    best = sorted(candidates, key=lambda x: x["score"], reverse=True)[0]

    # 5. Veo 프롬프트 + SEO 메타데이터 생성
    best["veo_prompts"] = generate_veo_prompt(best["product"], best["trend_reason"])
    best["seo_metadata"] = generate_seo_metadata(best["product"], best["score"], best["trend_reason"])
    best["analyzed_at"] = datetime.now().isoformat()

    print(f"\nTarget Selection Complete!")
    print(f"   Product: {best['product']}")
    print(f"   Commerce Score: {best['score']}/100")
    print(f"   Reason: {best['trend_reason']}")

    # 히스토리 저장
    os.makedirs(".agent/memory", exist_ok=True)
    history_path = ".agent/memory/trend_history.json"
    history = []
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            history = json.load(f)
    history.append(best)
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    return best


if __name__ == "__main__":
    result = run_trend_analysis()
    print("\nFinal Analysis Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
