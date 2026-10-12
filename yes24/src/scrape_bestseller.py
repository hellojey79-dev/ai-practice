"""YES24 국내도서 베스트셀러 전체 데이터 수집 및 CSV 저장 스크립트.

이 스크립트는 YES24 베스트셀러 웹 페이지에서 페이징 목록을 비동기식/동기식 엔드포인트로부터
1페이지부터 마지막 페이지까지 순차적으로 요청하여 도서 상세 정보 목록을 수집합니다.

[주요 기능]
1. 마지막 페이지 번호 자동 탐색:
   - 메인 베스트셀러 페이지의 페이징 네비게이션 버튼을 파싱하여 전체 페이지 수를 자동으로 계산합니다.
2. 페이지별 비동기 데이터 요청 (HTTP GET):
   - YES24 내부 API 엔드포인트(`BestSellerContents`)를 타겟으로 필요한 파라미터와 브라우저 헤더를 전송합니다.
   - 요청 간 0.1초~0.5초 사이 랜덤 지연시간(Random Delay)을 부여하여 대상 서버 부하 및 차단을 방지합니다.
3. 도서 메타데이터 상세 파싱:
   - 순위, 상품번호, 도서명, 부제목, 저자, 출판사, 출판일, 판매가, 정가, 할인율, 평점, 리뷰 수, 판매지수, 태그, 상품 URL, 이미지 URL 등 16개 항목 추출.
4. 중복 제거 및 증분 수집(Incremental Scraping):
   - 기존에 저장된 CSV 파일이 존재할 경우 상품번호(goods_no)를 키값으로 기존 데이터를 메모리에 적재한 뒤 신규 데이터와 병합합니다.
5. 중간 저장(Check-pointing):
   - 5페이지마다 CSV 파일로 중간 저장을 수행하여 장시간 수집 중 비정상 종료 시 데이터 유실을 방지합니다.

- 작성일: 2026-10-09
- 대상 경로: yes24/data/yes24_bestseller.csv
"""

import csv
import json
import os
import random
import re
import time
from typing import Any, Dict, List, Optional
import requests
from bs4 import BeautifulSoup


# ==============================================================================
# 1. 상수 및 기본 설정 정의
# ==============================================================================
# 베스트셀러 목록 데이터 비동기 요청 엔드포인트
BASE_URL = "https://www.yes24.com/product/category/BestSellerContents"

# 마지막 페이지 번호를 확인하기 위한 메인 베스트셀러 카테고리 URL (국내도서 종합)
MAIN_PAGE_URL = "https://www.yes24.com/product/category/bestseller?categoryNumber=001001003"

# 수집된 도서 데이터를 저장할 CSV 파일 상대 경로
CSV_PATH = os.path.join("yes24", "data", "yes24_bestseller.csv")

# 웹 크롤링 요청 시 사용할 브라우저 위장 공통 헤더
COMMON_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36 Edg/154.0.0.0"
    ),
    "sec-ch-ua": '"Chromium";v="154", "Microsoft Edge";v="154", "Not A(Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
}



def get_last_page_number() -> int:
    """메인 베스트셀러 페이지의 페이징 네비게이션 요소에서 마지막 페이지 번호를 추출합니다.

    YES24 카테고리 메인 페이지(HTML)를 조회하여 하단 페이지 번호 목록 중
    가장 마지막 페이지로 이동하는 '끝' 버튼(a.bgYUI.end 등)의 속성값을 파싱합니다.
    버튼이 없거나 파싱 중 예외가 발생할 경우 안전한 기본값(42)을 반환합니다.

    Returns:
        int: 탐색된 마지막 페이지 번호 (실패 시 기본값 42).
    """
    try:
        response = requests.get(MAIN_PAGE_URL, headers=COMMON_HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # 페이징의 마지막 페이지 이동 링크 탐색
            end_btn = soup.select_one("a.bgYUI.end, a.end")
            if end_btn:
                # 1) title 속성에 숫자(페이지 번호)가 직접 표기된 경우
                title_attr = end_btn.get("title", "")
                if title_attr.isdigit():
                    return int(title_attr)
                # 2) onclick 자바스크립트 함수 인자(예: goPage(42))에서 추출하는 경우
                onclick_attr = end_btn.get("onclick", "")
                match = re.search(r"\b(\d+)\b", onclick_attr)
                if match:
                    return int(match.group(1))
    except Exception as e:
        print(f"[알림] 마지막 페이지 확인 중 예외 발생, 기본값 42 사용: {e}")
    return 42


def load_existing_csv(csv_path: str) -> Dict[str, Dict[str, Any]]:
    """기존 CSV 파일이 존재하면 읽어서 상품번호를 키로 하는 딕셔너리로 반환합니다.

    중복 수집을 방지하고 이미 수집된 데이터를 보존하기 위해, 이전에 저장된 CSV 파일을 로드합니다.
    UTF-8-SIG 인코딩을 사용하여 Excel 등에서 한글이 깨지지 않도록 호환성을 유지합니다.

    Args:
        csv_path (str): 읽어올 기존 CSV 파일의 상대 또는 절대 경로.

    Returns:
        Dict[str, Dict[str, Any]]: 상품번호(goods_no)를 키로 하고, 도서 정보 딕셔너리를 값으로 가지는 맵.
    """
    existing_data: Dict[str, Dict[str, Any]] = {}
    if not os.path.exists(csv_path):
        print(f"[확인] 기존 CSV 파일이 없습니다. 새 파일로 생성합니다: {csv_path}")
        return existing_data

    try:
        with open(csv_path, mode="r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                goods_no = row.get("상품번호", "").strip()
                if goods_no:
                    existing_data[goods_no] = dict(row)
        print(f"[기존 데이터 로드] 기존 CSV에서 {len(existing_data)}건의 데이터를 불러왔습니다.")
    except Exception as e:
        print(f"[오류] 기존 CSV 파일 읽기 실패: {e}")
    return existing_data


def fetch_page_html(page_number: int) -> Optional[str]:
    """특정 페이지 번호의 베스트셀러 목록 비동기 HTML 조각을 요청하여 반환합니다.

    YES24 내부 AJAX 통신 규격에 맞는 파라미터(`categoryNumber`, `sumGb`, `pageNumber`, `pageSize` 등)와
    올바른 Referer 헤더를 포함하여 요청을 전송합니다.

    Args:
        page_number (int): 조회할 대상 페이지 번호 (1부터 시작).

    Returns:
        Optional[str]: 성공 시 응답 HTML 텍스트, HTTP 오류 또는 네트워크 오류 발생 시 None.
    """
    # YES24 베스트셀러 비동기 목록 조회 요청 파라미터 구성
    params = {
        "categoryNumber": "001001003",  # 국내도서 종합 카테고리 코드
        "sumGb": "06",                 # 집계 구분 (월간/주간/일간 등)
        "sex": "A",                    # 성별 전체
        "age": "255",                  # 연령 전체
        "goodsTp": "0",                # 상품 구분
        "addOptionTp": "0",            # 옵션 구분
        "excludeTp": "2",              # 제외 대상 구분
        "pageNumber": str(page_number),# 페이지 번호
        "pageSize": "24",              # 페이지당 출력 도서 수
        "goodsStatGb": "06",           # 상품 상태 구분
        "eBookTp": "0",                # 전자책 구분
        "bestType": "YES24_BESTSELLER",# 베스트셀러 유형
        "type": "",
        "saleYear": "0",
        "saleMonth": "0",
        "weekNo": "0",
        "saleDts": "",
        "viewMode": "",
        "freeYn": "",
    }

    # 브라우저 요청과 동일한 형태로 Referer 헤더 설정
    headers = dict(COMMON_HEADERS)
    headers["Referer"] = (
        f"https://www.yes24.com/product/category/bestseller"
        f"?categoryNumber=001001003&pageNumber={page_number}&pageSize=24"
    )

    try:
        response = requests.get(BASE_URL, params=params, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.text
        else:
            print(f"[요청 실패] 페이지 {page_number} 상태 코드: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"[네트워크 오류] 페이지 {page_number} 요청 실패: {e}")
        return None


def parse_bestseller_html(html_text: str) -> List[Dict[str, Any]]:
    """수신된 베스트셀러 HTML 조각에서 도서 상세 정보들을 추출합니다.

    각 도서 카드 요소(`li[data-goods-no]`)로부터 순위, 메타 정보, 가격, 평점, 태그 등을 파싱합니다.
    태그 누락이나 옵션 JSON 파싱 예외 발생 시 안전하게 기본 빈 문자열로 처리합니다.

    Args:
        html_text (str): YES24 서버로부터 수신한 HTML 응답 문자열.

    Returns:
        List[Dict[str, Any]]: 파싱된 도서 데이터 딕셔너리 리스트. 각 도서는 다음 키를 포함합니다:
            - 순위, 상품번호, 도서명, 부제목, 저자, 출판사, 출판일
            - 판매가, 정가, 할인율, 평점, 리뷰수, 판매지수
            - 태그, 상세URL, 이미지URL
    """
    soup = BeautifulSoup(html_text, "html.parser")
    # 상품 번호가 부여된 각 도서 리스트 항목 선택
    items = soup.select("li[data-goods-no]")

    books: List[Dict[str, Any]] = []

    for item in items:
        # 1. 고유 상품 번호
        goods_no = item.get("data-goods-no", "").strip()

        # 2. 순위 추출
        rank_elem = item.select_one("div.img_upper em.ico.rank")
        rank = rank_elem.get_text(strip=True) if rank_elem else ""

        # 3. 히든 필드의 옵션 JSON 정보 확인 (JSON에 정확한 정가/판매가/저자 정보가 포함되어 있음)
        opt_input = item.select_one("input[name='ORD_GOODS_OPT']")
        opt_data: Dict[str, Any] = {}
        if opt_input and opt_input.get("value"):
            try:
                opt_data = json.loads(opt_input["value"])
            except json.JSONDecodeError:
                opt_data = {}

        # 4. 도서명 및 상세 링크 URL
        name_elem = item.select_one("a.gd_name")
        title = ""
        detail_url = ""
        if name_elem:
            title = name_elem.get_text(strip=True)
            href = name_elem.get("href", "")
            detail_url = f"https://www.yes24.com{href}" if href.startswith("/") else href
        elif opt_data.get("goods_name"):
            title = opt_data.get("goods_name", "")

        # 5. 부제목 (한 줄 설명)
        sub_elem = item.select_one("span.gd_nameE")
        subtitle = sub_elem.get_text(strip=True) if sub_elem else ""

        # 6. 도서 표지 이미지 URL (지연 로딩 data-original 우선 처리)
        img_elem = item.select_one("img.lazy")
        image_url = ""
        if img_elem:
            image_url = img_elem.get("data-original") or img_elem.get("src") or ""

        # 7. 저자 정보 정제 (불필요한 태그/스크립트 제거)
        author = ""
        if opt_data.get("goodsAuth"):
            author = re.sub(r"[<>]", "", opt_data["goodsAuth"]).strip()
        else:
            auth_elem = item.select_one("span.authPub.info_auth")
            if auth_elem:
                for unneeded in auth_elem.select(".moreAuth, .moreAuthLi, .moreRatingArea, script"):
                    unneeded.decompose()
                author = re.sub(r"\s+", " ", auth_elem.get_text(" ", strip=True))

        # 8. 출판사
        pub_elem = item.select_one("span.authPub.info_pub")
        publisher = pub_elem.get_text(strip=True) if pub_elem else ""

        # 9. 출판일
        date_elem = item.select_one("span.authPub.info_date")
        pub_date = date_elem.get_text(strip=True) if date_elem else ""

        # 10. 가격 정보 (판매가, 정가, 할인율 - 콤마 제거)
        sale_elem = item.select_one("div.info_price strong.txt_num em.yes_b")
        sale_price = ""
        if sale_elem:
            sale_price = sale_elem.get_text(strip=True).replace(",", "")
        elif opt_data.get("salePrice") is not None:
            sale_price = str(int(opt_data["salePrice"]))

        fixed_elem = item.select_one("div.info_price span.txt_num.dash em.yes_m")
        fixed_price = ""
        if fixed_elem:
            fixed_price = fixed_elem.get_text(strip=True).replace(",", "")
        elif opt_data.get("shopPrice") is not None:
            fixed_price = str(int(opt_data["shopPrice"]))

        discount_elem = item.select_one("div.info_price span.txt_sale em.num")
        discount_rate = f"{discount_elem.get_text(strip=True)}%" if discount_elem else ""

        # 11. 평점 및 리뷰 수
        rating_elem = item.select_one("span.rating_grade em.yes_b")
        rating = rating_elem.get_text(strip=True) if rating_elem else ""

        review_elem = item.select_one("span.rating_rvCount em.txC_blue")
        review_count = review_elem.get_text(strip=True) if review_elem else ""

        # 12. 판매지수 (숫자만 추출)
        sales_elem = item.select_one("span.saleNum")
        sales_index = ""
        if sales_elem:
            text = sales_elem.get_text(strip=True)
            match = re.search(r"[\d,]+", text)
            if match:
                sales_index = match.group(0).replace(",", "")

        # 13. 태그 키워드 목록 (쉼표 구분 결합)
        tags = [tag.get_text(strip=True) for tag in item.select("div.info_tag span.tag a")]
        tag_str = ", ".join(tags)

        # 도서 데이터 딕셔너리 생성
        books.append({
            "순위": rank,
            "상품번호": goods_no,
            "도서명": title,
            "부제목": subtitle,
            "저자": author,
            "출판사": publisher,
            "출판일": pub_date,
            "판매가": sale_price,
            "정가": fixed_price,
            "할인율": discount_rate,
            "평점": rating,
            "리뷰수": review_count,
            "판매지수": sales_index,
            "태그": tag_str,
            "상세URL": detail_url,
            "이미지URL": image_url,
        })

    return books


def save_books_to_csv(books: List[Dict[str, Any]], output_path: str) -> None:
    """도서 목록을 순위(1순위) 기준으로 정렬하여 UTF-8-SIG CSV 파일로 저장합니다.

    디렉터리가 존재하지 않는 경우 상위 폴더를 자동 생성하며, 일관된 순서로 CSV 필드를 작성합니다.

    Args:
        books (List[Dict[str, Any]]): 저장할 도서 데이터 목록.
        output_path (str): 출력할 CSV 파일 상대/절대 경로.
    """
    if not books:
        print("[경고] 저장할 데이터가 없습니다.")
        return

    # 순위 기준 정렬 함수 (숫자로 변환 가능한 경우 정수 우선, 불가능할 경우 문자열 기준)
    def parse_rank_key(item: Dict[str, Any]):
        r = item.get("순위", "")
        try:
            return (0, int(r))
        except (ValueError, TypeError):
            return (1, str(r))

    sorted_books = sorted(books, key=parse_rank_key)

    # 출력 대상 상위 폴더 생성
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # CSV 헤더 컬럼 순서 지정
    fieldnames = [
        "순위", "상품번호", "도서명", "부제목", "저자", "출판사", "출판일",
        "판매가", "정가", "할인율", "평점", "리뷰수", "판매지수", "태그",
        "상세URL", "이미지URL"
    ]

    with open(output_path, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_books)


def main() -> None:
    """YES24 베스트셀러 전권 수집 프로세스를 총괄 실행합니다.

    실행 순서:
    1. 기존 CSV 데이터를 로드하여 중복 수집 방지 준비
    2. 메인 페이지를 조회하여 전체 마지막 페이지 번호 파악
    3. 1페이지부터 마지막 페이지까지 순차 요청 (0.1~0.5초 랜덤 대기)
    4. 페이지 응답 HTML 파싱 및 신규 도서 정보 메모리 병합
    5. 5페이지 주기로 중간 저장(Check-point) 수행
    6. 전체 수집 완료 후 최종 정렬된 CSV 파일 저장 및 통계 출력
    """
    # 1. 기존 CSV 데이터 로드
    book_dict = load_existing_csv(CSV_PATH)

    # 2. 마지막 페이지 번호 자동 탐색
    last_page = get_last_page_number()
    print(f"[수집 계획] 1페이지부터 {last_page}페이지까지 수집을 진행합니다.")

    new_books_count = 0

    # 3. 1페이지부터 마지막 페이지까지 순회 수집
    for page in range(1, last_page + 1):
        # 서버 과부하 방지 및 차단 예방을 위한 0.1초~0.5초 랜덤 지연시간
        delay = random.uniform(0.1, 0.5)
        time.sleep(delay)

        html = fetch_page_html(page)
        if not html:
            print(f"[{page}/{last_page} 페이지] 응답 없음 또는 오류. 다음 페이지로 진행합니다.")
            continue

        page_books = parse_bestseller_html(html)
        if not page_books:
            print(f"[{page}/{last_page} 페이지] 도서 아이템 없음. 마지막 페이지 도달로 판단하여 중단합니다.")
            break

        added_in_page = 0
        for book in page_books:
            goods_no = book["상품번호"]
            # 신규 도서 확인 및 기존 도서 순위/정보 최신화
            if goods_no not in book_dict:
                book_dict[goods_no] = book
                added_in_page += 1
                new_books_count += 1
            else:
                # 이미 존재하더라도 최신 파싱 정보로 업데이트
                book_dict[goods_no] = book

        print(
            f"[{page:02d}/{last_page} 페이지] 수집 도서: {len(page_books)}권 "
            f"(신규 추가: {added_in_page}권, 대기시간: {delay:.2f}초)"
        )

        # 5페이지마다 주기적 중간 저장 (중간 장애 발생 시 데이터 손실 최소화)
        if page % 5 == 0:
            save_books_to_csv(list(book_dict.values()), CSV_PATH)

    # 4. 전체 수집 완료 후 최종 정렬 저장
    final_books = list(book_dict.values())
    save_books_to_csv(final_books, CSV_PATH)

    print("\n" + "=" * 50)
    print(f"[수집 완료] 총 {len(final_books)}권의 도서 정보가 저장되었습니다.")
    print(f"[신규 추가] 이번 실행으로 추가/갱신된 신규 도서: {new_books_count}권")
    print(f"[저장 경로] {CSV_PATH}")
    print("=" * 50)


if __name__ == "__main__":
    main()

