"""범용 하이브리드 웹 크롤러 표준 템플릿.

이 모듈은 새로운 웹사이트를 크롤링할 때 복사하여 사용할 수 있는 표준 골격입니다.
API 엔드포인트 역공학(JSON) 호출과 HTML 파싱(BeautifulSoup)을 모두 지원하며,
요청 지연시간, 재시도 로직, 에러 핸들링, 데이터프레임 변환 및 CSV/JSON 이중 저장을
완벽히 지원합니다.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import random
import sys
import time
from typing import Any

import pandas as pd
import requests

# Windows 콘솔 인코딩 대응
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# 표준 브라우저 User-Agent 리스트
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
]


class BaseScraper:
    """범용 웹 수집 기본 클래스."""

    def __init__(self, output_dir: Path, delay_range: tuple[float, float] = (0.5, 1.2)):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.delay_range = delay_range
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        })

    def request_with_retry(self, url: str, method: str = "GET", params: dict[str, Any] | None = None,
                           headers: dict[str, str] | None = None, max_retries: int = 3) -> requests.Response | None:
        """지연시간 및 재시도를 포함하여 안전하게 HTTP 요청을 보냅니다."""
        for attempt in range(1, max_retries + 1):
            try:
                # 서버 부하 방지용 지연시간
                time.sleep(random.uniform(*self.delay_range))
                resp = self.session.request(method, url, params=params, headers=headers, timeout=12)
                resp.raise_for_status()
                return resp
            except requests.RequestException as e:
                print(f"[경고] 요청 실패 ({attempt}/{max_retries}): {e}")
                time.sleep(attempt * 1.5)
        return None

    def parse_item(self, raw_data: Any) -> dict[str, Any]:
        """개별 데이터 항목 파싱 (서브클래스에서 재정의 필요)."""
        raise NotImplementedError("parse_item 메서드를 구현해야 합니다.")

    def run(self, max_pages: int = 10) -> list[dict[str, Any]]:
        """전체 수집 프로세스 실행 (서브클래스에서 재정의)."""
        print(f"[안내] 수집 파이프라인 가동 (최대 {max_pages}페이지)")
        items: list[dict[str, Any]] = []
        # 샘플 골격: 실제 구현 시 사이트 API/HTML에 맞춰 작성
        return items

    def save_results(self, items: list[dict[str, Any]], prefix: str = "scraped_data") -> tuple[Path, Path]:
        """수집된 결과를 CSV 및 JSON으로 동시에 영구 저장합니다."""
        today_str = datetime.now().strftime("%Y%m%d")
        csv_file = self.output_dir / f"{prefix}_{today_str}.csv"
        json_file = self.output_dir / f"{prefix}_{today_str}.json"

        # JSON 저장
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

        # CSV 저장
        df = pd.DataFrame(items)
        df.to_csv(csv_file, index=False, encoding="utf-8-sig")

        print("=" * 60)
        print(f"🎉 [저장 완료] 총 {len(items):,}건 적재 성공")
        print(f"  - CSV:  {csv_file}")
        print(f"  - JSON: {json_file}")
        print("=" * 60)

        return csv_file, json_file


def main() -> None:
    """메인 실행 함수."""
    parser = argparse.ArgumentParser(description="범용 웹 크롤러 실행기")
    parser.add_argument("--output-dir", type=str, default="harness/data", help="저장 디렉터리")
    parser.add_argument("--prefix", type=str, default="sample_site", help="파일 이름 접두어")
    parser.add_argument("--max-pages", type=int, default=5, help="수집 최대 페이지 수")
    args = parser.parse_args()

    scraper = BaseScraper(output_dir=Path(args.output_dir))
    items = scraper.run(max_pages=args.max_pages)
    if items:
        scraper.save_results(items, prefix=args.prefix)
    else:
        print("[안내] 수집된 데이터가 없습니다. parse_item 및 run 구현을 확인하세요.")


if __name__ == "__main__":
    main()
