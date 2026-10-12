# 📚 교보문고 IT/컴퓨터 분야 베스트셀러 스크래핑 최종 작업 명세서

## 1. 개요 및 목적
- **목적**: 교보문고 **IT/컴퓨터** 분야의 베스트셀러 전체 도서 목록을 공식 API 엔드포인트를 통해 빠르고 안정적으로 수집하여 데이터셋(CSV 및 JSON)을 구축합니다.
- **역할**: 웹 스크래핑 및 데이터 파이프라인 개발 엔지니어

---

## 2. API 엔드포인트 및 호출 규격

- **Base URL**: `https://store.kyobobook.co.kr/api/gw/best/best-seller/online`
- **HTTP Method**: `GET`
- **쿼리 파라미터 (Query Parameters)**:
  - `page`: 페이지 번호 (1부터 시작)
  - `per`: 페이지당 도서 수 (`20`)
  - `period`: `001` (주간/현재 기준 베스트)
  - `dsplDvsnCode`: `001`
  - `dsplTrgtDvsnCode`: `004` (온라인 베스트)
  - `saleCmdtClstCode`: `33` (컴퓨터/IT 분야)
- **페이징 처리**:
  - 첫 번째 페이지(`page=1`) 호출 시 응답의 `data.total` 값(약 410건)을 확인하여 전체 페이지 수(`ceil(total / per)`)를 동적으로 계산하고 마지막 페이지까지 순회 수집합니다.

---

## 3. 데이터 스키마 및 매핑 규칙

API 응답 JSON의 `data.bestSeller` 배열 각 항목을 아래 스키마로 가공하여 저장합니다:

| 필드명 | 데이터 타입 | 원본 API 필드 | 설명 / 가공 규칙 | 예시 |
| :--- | :--- | :--- | :--- | :--- |
| `rank` | Integer | `prstRnkn` | 현재 순위 | `1` |
| `title` | String | `cmdtName` | 도서명 (HTML 태그 제거) | `2026 이지패스 ADsP 데이터분석 준전문가` |
| `author` | String | `chrcName` | 저자 / 역자 | `박현민 외` |
| `publisher` | String | `pbcmName` | 출판사 | `위키북스` |
| `pub_date` | String | `rlseDate` | 출간일 (`YYYYMMDD` -> `YYYY-MM-DD` 변환) | `2026-01-02` |
| `original_price` | Integer | `price` | 정가 (원) | `30000` |
| `sale_price` | Integer | `sapr` | 판매가 / 할인가 (원) | `27000` |
| `discount_rate` | Integer | `dscnRate` | 할인율 (%) | `10` |
| `rating` | Float | `buyRevwRvgr` | 평점 (결측 시 `0.0`) | `9.86` |
| `review_count` | Integer | `buyRevwNumc` | 리뷰 수 (결측 시 `0`) | `395` |
| `isbn` | String | `cmdtCode` | ISBN | `9791158396510` |
| `category_name` | String | `saleCmdtClstName` | 카테고리명 | `컴퓨터/IT` |
| `category_code` | String | `saleCmdtClstCode` | 카테고리 코드 | `33280909` |
| `inbukCntt` | String | `inbukCntt` | 책 상세 설명 (HTML 태그 제거 및 줄바꿈 보존 정제) | `미어캣 2026 최신 기출문제 수록...` |
| `link` | String | `saleCmdtid` | 도서 상세 페이지 URL 조합 | `https://product.kyobobook.co.kr/detail/{saleCmdtid}` |

---

## 4. 환경 및 저장 규칙

- **실행 환경**:
  - 프로젝트 루트의 공통 가상환경(`.venv`) 사용
  - 패키지 및 실행은 `uv` 기준 (`uv add requests pandas`, `uv run python kyobooks/src/scraper.py`)
- **저장 디렉터리 및 파일 명명**:
  - 저장 위치: `kyobooks/data/` (상대경로)
  - 파일 형식: **CSV 및 JSON 동시 저장**
  - 파일명 규칙:
    - CSV: `kyobooks/data/kyobo_it_bestsellers_YYYYMMDD.csv` (`utf-8-sig` 인코딩)
    - JSON: `kyobooks/data/kyobo_it_bestsellers_YYYYMMDD.json` (`ensure_ascii=False`, `indent=2`)

---

## 5. 스크립트 설계 (`kyobooks/src/scraper.py`)

- **CLI 옵션 (`argparse`) 지원**:
  - `--max-pages`: 수집할 최대 페이지 수 제한 (기본값: `None` -> 전체 수집)
  - `--delay`: 요청 간 지연 시간 (초 단위, 기본값: `1.0`)
- **안정성 및 로깅**:
  - 표준 데스크톱 `User-Agent` 및 요청 헤더 적용
  - 페이지별 수집 현황(`[페이지 X/Y] N권 수집 완료`) 실시간 콘솔 출력
  - 완료 시 총 수집 건수 및 저장된 파일 경로 출력
