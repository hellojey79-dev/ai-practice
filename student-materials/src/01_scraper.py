"""교보문고 IT/컴퓨터 베스트셀러 데이터 수집 실습 스크립트.

이 스크립트는 교보문고 공식 REST API 엔드포인트를 호출하여 IT/컴퓨터 분야 베스트셀러 도서
목록을 수집하고, 정제 과정을 거쳐 CSV 및 JSON 파일로 저장하는 데이터 수집 실습용 코드입니다.

주요 기능:
1. 교보문고 베스트셀러 REST API 호출 및 페이징 처리
2. HTML 태그 제거 및 텍스트/날짜 데이터 표준화 정제
3. 요청 지연(Rate Limiting) 및 차단 방지 헤더 적용
4. CSV(utf-8-sig) 및 JSON 동시 저장

작성자: ai-practice 데이터 엔지니어링 튜터
생성일: 2026-10-14
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import math
from pathlib import Path
import re
import sys
import time
from typing import Any

# Windows 콘솔 인코딩 문제 방지
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import pandas as pd
import requests

# ==============================================================================
# 1. API 엔드포인트 및 요청 설정
# ==============================================================================
API_URL = "https://store.kyobobook.co.kr/api/gw/best/best-seller/online"
IT_CATEGORY_CODE = "33"  # 교보문고 컴퓨터/IT 분야 분류 코드

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://product.kyobobook.co.kr/",
}


# ==============================================================================
# 2. 텍스트 정제 헬퍼 함수
# ==============================================================================
def clean_html(raw_html: str | None) -> str:
    """HTML 태그(<mark>, <b> 등)를 제거하고 불필요한 공백을 정돈합니다."""
    if not raw_html:
        return ""
    text = re.sub(r"<[^>]+>", "", str(raw_html))
    return " ".join(text.split())


def clean_intro_text(raw_text: str | None) -> str:
    """책 상세 설명(inbukCntt)의 줄바꿈 태그를 개행문자로 보존하며 HTML을 정제합니다."""
    if not raw_text:
        return ""
    # <br>, <p> 태그를 줄바꿈으로 치환
    text = re.sub(r"(?i)<br\s*/?>", "\n", str(raw_text))
    text = re.sub(r"(?i)</?p\s*>", "\n", text)
    # 기타 잔여 HTML 태그 제거
    text = re.sub(r"<[^>]+>", "", text)
    # 3개 이상의 연속 개행을 2개로 정리
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def format_date(raw_date: str | None) -> str:
    """YYYYMMDD 형식의 문자열을 YYYY-MM-DD 표준 날짜 형식으로 변환합니다."""
    if not raw_date:
        return ""
    raw_date = str(raw_date).strip()
    if len(raw_date) == 8 and raw_date.isdigit():
        return f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
    return raw_date


# ==============================================================================
# 3. API 호출 및 파싱 로직
# ==============================================================================
def fetch_bestseller_page(
    page: int,
    per: int = 20,
    category_code: str = IT_CATEGORY_CODE,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    """지정된 페이지의 베스트셀러 목록 JSON 데이터를 API에서 호출합니다."""
    client = session or requests.Session()
    params = {
        "page": page,
        "per": per,
        "period": "001",           # 주간/실시간 온라인 베스트
        "dsplDvsnCode": "001",
        "dsplTrgtDvsnCode": "004",   # 온라인 베스트
        "saleCmdtClstCode": category_code,
    }
    response = client.get(API_URL, params=params, headers=DEFAULT_HEADERS, timeout=10)
    response.raise_for_status()
    return response.json()


def parse_book_item(item: dict[str, Any]) -> dict[str, Any]:
    """API 응답 단일 항목을 분석용 표준 딕셔너리로 변환합니다."""
    sale_cmdt_id = item.get("saleCmdtid") or ""
    detail_url = (
        f"https://product.kyobobook.co.kr/detail/{sale_cmdt_id}"
        if sale_cmdt_id
        else ""
    )

    return {
        "rank": int(item.get("prstRnkn") or 0),
        "title": clean_html(item.get("cmdtName")),
        "author": clean_html(item.get("chrcName")),
        "publisher": clean_html(item.get("pbcmName")),
        "pub_date": format_date(item.get("rlseDate")),
        "original_price": int(item.get("price") or 0),
        "sale_price": int(item.get("sapr") or 0),
        "discount_rate": int(item.get("dscnRate") or 0),
        "rating": float(item.get("buyRevwRvgr") or 0.0),
        "review_count": int(item.get("buyRevwNumc") or 0),
        "isbn": str(item.get("cmdtCode") or "").strip(),
        "category_name": str(item.get("saleCmdtClstName") or "컴퓨터/IT").strip(),
        "category_code": str(item.get("saleCmdtClstCode") or "").strip(),
        "inbukCntt": clean_intro_text(item.get("inbukCntt")),
        "link": detail_url,
    }


def crawl_bestsellers(
    max_pages: int | None = 5,
    delay: float = 1.0,
    per: int = 20,
) -> list[dict[str, Any]]:
    """지정된 페이지 수(기본: 5페이지, 약 100권)까지 베스트셀러를 순회 수집합니다."""
    books: list[dict[str, Any]] = []
    session = requests.Session()

    print("[1/3] 교보문고 IT/컴퓨터 베스트셀러 API 연결 중...")
    first_resp = fetch_bestseller_page(page=1, per=per, session=session)
    data = first_resp.get("data", {})
    total_count = int(data.get("total") or 0)
    calc_pages = math.ceil(total_count / per) if total_count > 0 else 1

    target_pages = min(calc_pages, max_pages) if max_pages else calc_pages
    print(f"  - 전체 등록 도서: {total_count:,}권 (전체 {calc_pages}페이지 중 {target_pages}페이지 수집)")

    # 1페이지 파싱
    for item in data.get("bestSeller", []):
        books.append(parse_book_item(item))
    print(f"  [페이지 1/{target_pages}] {len(books)}권 수집 완료")

    # 2페이지부터 순회
    for cur_page in range(2, target_pages + 1):
        time.sleep(delay)  # 예의 있는 크롤링을 위한 지연 시간
        try:
            page_data = fetch_bestseller_page(page=cur_page, per=per, session=session)
            items = page_data.get("data", {}).get("bestSeller", [])
            for item in items:
                books.append(parse_book_item(item))
            print(f"  [페이지 {cur_page}/{target_pages}] 누적 {len(books)}권 수집 완료")
        except Exception as e:
            print(f"  [경고] {cur_page}페이지 수집 실패: {e}")

    return books


# ==============================================================================
# 4. 파일 영속화 로직
# ==============================================================================
def save_data(books: list[dict[str, Any]], output_dir: Path) -> tuple[Path, Path]:
    """수집된 도서 목록을 CSV(utf-8-sig) 및 JSON으로 저장합니다."""
    output_dir.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now().strftime("%Y%m%d")

    csv_path = output_dir / f"kyobo_it_bestsellers_{today_str}.csv"
    json_path = output_dir / f"kyobo_it_bestsellers_{today_str}.json"

    # CSV 저장
    df = pd.DataFrame(books)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    # JSON 저장
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

    return csv_path, json_path


# ==============================================================================
# 5. CLI 메인 진입점
# ==============================================================================
def main() -> None:
    """메인 실행 함수."""
    parser = argparse.ArgumentParser(description="교보문고 IT 베스트셀러 크롤링 실습")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=5,
        help="수집할 최대 페이지 수 (기본값: 5 -> 상위 100권, 전체 수집 시 0 입력)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="요청 간 대기 시간 (초, 기본값: 1.0)",
    )
    args = parser.parse_args()

    max_p = None if args.max_pages <= 0 else args.max_pages

    # student-materials 기준 상대경로
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"

    print("=" * 60)
    print("🚀 [Step 1] 교보문고 IT 베스트셀러 데이터 수집 실습 시작")
    print("=" * 60)

    books = crawl_bestsellers(max_pages=max_p, delay=args.delay)

    if not books:
        print("[실패] 수집된 도서가 없습니다.")
        return

    csv_p, json_p = save_data(books, data_dir)
    print("\n[완료] 데이터 수집 및 파일 저장이 완료되었습니다!")
    print(f"- 수집 도서 수: {len(books):,}권")
    print(f"- CSV 저장 경로: {csv_p}")
    print(f"- JSON 저장 경로: {json_p}")


if __name__ == "__main__":
    main()
