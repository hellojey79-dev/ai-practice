"""교보문고 IT/컴퓨터 베스트셀러 도서 데이터 수집 스크립트.

교보문고 공식 REST API 엔드포인트를 호출하여 도서 목록을 수집하고,
CSV 및 JSON 파일로 상대경로 kyobooks/data/ 디렉터리에 저장합니다.
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

# 교보문고 베스트셀러 API 기본 URL
API_URL = "https://store.kyobobook.co.kr/api/gw/best/best-seller/online"

# 컴퓨터/IT 분야 분류 코드
IT_CATEGORY_CODE = "33"

# 표준 요청 헤더
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


def clean_html(raw_html: str | None) -> str:
    """HTML 태그를 제거하고 공백을 정돈합니다."""
    if not raw_html:
        return ""
    text = re.sub(r"<[^>]+>", "", raw_html)
    return " ".join(text.split())


def clean_intro_text(raw_text: str | None) -> str:
    """책 상세 설명(inbukCntt) 텍스트를 정제합니다. 줄바꿈을 보존하고 HTML 태그를 제거합니다."""
    if not raw_text:
        return ""
    # <br>, <p> 태그를 줄바꿈으로 치환
    text = re.sub(r"(?i)<br\s*/?>", "\n", raw_text)
    text = re.sub(r"(?i)</?p\s*>", "\n", text)
    # 기타 HTML 태그 제거
    text = re.sub(r"<[^>]+>", "", text)
    # 3개 이상의 연속 개행을 2개로 정리
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def format_date(raw_date: str | None) -> str:
    """YYYYMMDD 문자열을 YYYY-MM-DD 형식으로 변환합니다."""
    if not raw_date:
        return ""
    raw_date = raw_date.strip()
    if len(raw_date) == 8 and raw_date.isdigit():
        return f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
    return raw_date


def fetch_bestseller_page(
    page: int,
    per: int = 20,
    category_code: str = IT_CATEGORY_CODE,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    """특정 페이지의 베스트셀러 도서 목록 데이터를 API에서 호출합니다."""
    client = session or requests.Session()
    params = {
        "page": page,
        "per": per,
        "period": "001",
        "dsplDvsnCode": "001",
        "dsplTrgtDvsnCode": "004",
        "saleCmdtClstCode": category_code,
    }
    response = client.get(API_URL, params=params, headers=DEFAULT_HEADERS, timeout=10)
    response.raise_for_status()
    return response.json()


def parse_book_item(item: dict[str, Any]) -> dict[str, Any]:
    """API 응답의 개별 도서 항목을 정제된 딕셔너리로 변환합니다."""
    sale_cmdt_id = item.get("saleCmdtid") or ""
    detail_url = (
        f"https://product.kyobobook.co.kr/detail/{sale_cmdt_id}"
        if sale_cmdt_id
        else ""
    )

    intro_content = clean_intro_text(item.get("inbukCntt"))

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
        "inbukCntt": intro_content,  # 원본 API 키값 명시 (책 상세 설명)
        "link": detail_url,
    }


def crawl_kyobo_it_bestsellers(
    max_pages: int | None = None,
    delay: float = 1.0,
    per: int = 20,
) -> list[dict[str, Any]]:
    """교보문고 IT/컴퓨터 베스트셀러 도서 목록을 전체 또는 지정된 페이지까지 수집합니다."""
    books: list[dict[str, Any]] = []
    session = requests.Session()

    print("[시작] 교보문고 IT/컴퓨터 베스트셀러 수집을 시작합니다...")

    # 1페이지 호출하여 전체 도서 수 및 페이지 수 파악
    first_response = fetch_bestseller_page(page=1, per=per, session=session)
    data = first_response.get("data", {})
    total_count = int(data.get("total") or 0)
    calculated_pages = math.ceil(total_count / per) if total_count > 0 else 1

    total_pages_to_fetch = (
        min(calculated_pages, max_pages) if max_pages else calculated_pages
    )

    print(
        f"[정보] 총 도서 수: {total_count}권 | 전체 페이지 수: {calculated_pages}페이지 "
        f"(수집 대상: {total_pages_to_fetch}페이지)"
    )

    # 1페이지 파싱
    for item in data.get("bestSeller", []):
        books.append(parse_book_item(item))
    print(f"  [페이지 1/{total_pages_to_fetch}] {len(books)}권 수집 완료")

    # 2페이지부터 순회 수집
    for current_page in range(2, total_pages_to_fetch + 1):
        time.sleep(delay)
        try:
            page_data = fetch_bestseller_page(page=current_page, per=per, session=session)
            items = page_data.get("data", {}).get("bestSeller", [])
            for item in items:
                books.append(parse_book_item(item))
            print(
                f"  [페이지 {current_page}/{total_pages_to_fetch}] "
                f"누적 {len(books)}권 수집 완료"
            )
        except Exception as e:
            print(f"  [오류] [페이지 {current_page}] 수집 중 오류 발생: {e}")

    return books


def save_books_data(books: list[dict[str, Any]], output_dir: Path) -> tuple[Path, Path]:
    """수집된 도서 목록을 CSV 및 JSON 파일로 저장합니다."""
    output_dir.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now().strftime("%Y%m%d")

    csv_path = output_dir / f"kyobo_it_bestsellers_{today_str}.csv"
    json_path = output_dir / f"kyobo_it_bestsellers_{today_str}.json"

    # CSV 저장 (utf-8-sig 로 한글 깨짐 방지)
    df = pd.DataFrame(books)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    # JSON 저장
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

    return csv_path, json_path


def main() -> None:
    """메인 실행 함수."""
    parser = argparse.ArgumentParser(
        description="교보문고 IT/컴퓨터 베스트셀러 도서 목록 수집기"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="수집할 최대 페이지 수 (미지정 시 전체 페이지 수집)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="요청 간 지연 시간 (초 단위, 기본값: 1.0)",
    )
    parser.add_argument(
        "--per",
        type=int,
        default=20,
        help="페이지당 도서 수 (기본값: 20)",
    )
    args = parser.parse_args()

    # 스크립트 위치 기준으로 프로젝트 루트 및 상대 데이터 디렉터리 경로 설정
    base_dir = Path(__file__).resolve().parent.parent  # kyobooks 디렉터리
    data_dir = base_dir / "data"

    books = crawl_kyobo_it_bestsellers(
        max_pages=args.max_pages,
        delay=args.delay,
        per=args.per,
    )

    if not books:
        print("[실패] 수집된 도서 데이터가 없습니다.")
        return

    csv_path, json_path = save_books_data(books, data_dir)
    print("\n[완료] 데이터 수집 및 저장이 성공적으로 완료되었습니다!")
    print(f"- 총 수집 도서: {len(books)}권")
    print(f"- CSV 파일  : {csv_path}")
    print(f"- JSON 파일 : {json_path}")


if __name__ == "__main__":
    main()
