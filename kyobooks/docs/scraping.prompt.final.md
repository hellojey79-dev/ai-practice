# 📚 교보문고 IT/컴퓨터 분야 베스트셀러 스크래핑 및 분석 최종 작업 지시서

- **문서 버전**: v1.0 (최종 통합본)
- **최종 수정일**: 2026-10-13
- **통합 대상**: `kyobooks/docs/scraping.prompt.md` + `kyobooks/docs/scraping.prompt.backup.md`
- **상태**: 승인 및 실행 표준 (Official Standard)

---

## 1. 개요 및 목적 (Overview & Objectives)

### 1.1 목적
교보문고 **IT/컴퓨터** 분야의 베스트셀러 및 주요 도서 정보를 공식 API 엔드포인트를 통해 빠르고 안정적으로 전수 수집하고, 수집된 데이터를 바탕으로 기술 트렌드 분석, 가격 분포, 출판 시장 점유율, 독자 반응(평점/리뷰) 분석 및 시각화 데이터셋(CSV, JSON, EDA 차트, 리포트)을 구축합니다.

### 1.2 담당 역할
- **웹 스크래핑 및 데이터 엔지니어링**: REST API 통신, 크롤링 안정성 확보, 데이터 정제 및 영속화
- **데이터 분석가(EDA)**: 데이터 무결성 검증, 텍스트(TF-IDF) 마이닝, 다변량 시각화 차트 생성 및 비즈니스 인사이트 도출

---

## 2. 수집 대상 범위 및 전략 (Scope & Strategy)

- **타깃 카테고리**: 교보문고 국내도서 > **IT/컴퓨터** (분야 코드: `33`)
- **수집 방식**: 교보문고 공식 게이트웨이 REST API 직접 호출 (JSON 응답 파싱)
- **수집 분량**:
  - **전수 수집 (기본값)**: 1페이지 호출 시 반환되는 `data.total` 값(약 410~500권)을 기반으로 전체 페이지 동적 계산 후 전수 수집
  - **부분 수집 (옵션)**: CLI 인자(`--max-pages`)를 통한 상위 N페이지(예: 1~5페이지, 상위 100권) 제한 수집 지원

---

## 3. API 엔드포인트 및 호출 규격 (API Specifications)

### 3.1 베스트셀러 목록 수집 API (검증 완료 ✅)
- **Base URL**: `https://store.kyobobook.co.kr/api/gw/best/best-seller/online`
- **HTTP Method**: `GET`
- **쿼리 파라미터 (Query Parameters)**:
  | 파라미터명 | 타입 | 기본값 | 설명 | 상태 |
  | :--- | :---: | :---: | :--- | :---: |
  | `page` | Integer | `1` | 요청 페이지 번호 (1부터 시작) | 검증 완료 ✅ |
  | `per` | Integer | `20` | 페이지당 도서 수 (교보문고 기본 단위) | 검증 완료 ✅ |
  | `period` | String | `001` | 집계 주기 코드 (`001`: 주간/실시간 온라인 베스트) | 검증 완료 ✅ |
  | `dsplDvsnCode` | String | `001` | 전시 구분 코드 | 검증 완료 ✅ |
  | `dsplTrgtDvsnCode` | String | `004` | 전시 대상 구분 코드 (`004`: 온라인 베스트) | 검증 완료 ✅ |
  | `saleCmdtClstCode` | String | `33` | 상품 분류 코드 (`33`: IT/컴퓨터 분야) | 검증 완료 ✅ |

- **페이징 동적 계산 로직**:
  1. `page=1` 호출 후 응답의 `data.total` 값(정수) 추출
  2. 전체 페이지 수 계산: `total_pages = ceil(total / per)`
  3. `max_pages` 인자가 지정된 경우 `min(total_pages, max_pages)`로 대상 페이지 확정 후 순회

### 3.2 도서 상세 및 세부 분류 조회 API (⚠️ 검증 필요)
- **Base URL**: `https://product.kyobobook.co.kr/api/gw/pub/pdt/detail/{saleCmdtid}` (추정)
- **용도**: 목록 API에서 제공되지 않는 상세 텍스트 세부 카테고리(`sub_category`: 예: '인공지능', '웹개발' 등) 및 목차, 상세 소개 추가 수집용
- **주의사항**: 
  > [!WARNING]
  > 해당 상세 API 주소 및 필드 규격은 현재 목록 수집 파이프라인에 포함되어 있지 않으며, 호출 시 추가 트래픽이 발생하므로 **사전 엔드포인트 유효성 검증(HTTP 200, 스키마 일치 여부) 후 도입**해야 합니다.

---

## 4. 데이터 스키마 및 매핑 규칙 (Data Schema & Mapping)

API 응답 JSON의 `data.bestSeller` 배열 각 항목을 아래 스키마로 표준화하여 저장합니다.

### 4.1 수집 데이터 필드 명세 (15개 필드)
| No | 필드명 | 데이터 타입 | 원본 API 필드 | 설명 및 전처리/가공 규칙 | 예시 | 상태 |
| :-: | :--- | :---: | :--- | :--- | :--- | :---: |
| 1 | `rank` | Integer | `prstRnkn` | 현재 베스트셀러 순위 (결측 시 `0`) | `1` | 검증 완료 ✅ |
| 2 | `title` | String | `cmdtName` | 도서명 (HTML 태그 제거, 부제목 포함) | `2026 이지패스 ADsP 데이터분석 준전문가` | 검증 완료 ✅ |
| 3 | `author` | String | `chrcName` | 저자 / 역자 (HTML 태그 제거) | `박현민 외` | 검증 완료 ✅ |
| 4 | `publisher` | String | `pbcmName` | 출판사 (HTML 태그 제거) | `위키북스` | 검증 완료 ✅ |
| 5 | `pub_date` | String | `rlseDate` | 출간일 (`YYYYMMDD` -> `YYYY-MM-DD` 표준 포맷 변환) | `2026-01-02` | 검증 완료 ✅ |
| 6 | `original_price` | Integer | `price` | 정가 (원 단위 정수형 변환, 결측 시 `0`) | `30000` | 검증 완료 ✅ |
| 7 | `sale_price` | Integer | `sapr` | 판매가/할인가 (원 단위 정수형 변환, 결측 시 `0`) | `27000` | 검증 완료 ✅ |
| 8 | `discount_rate` | Integer | `dscnRate` | 할인율 (% 단위 정수형, 결측 시 `0`) | `10` | 검증 완료 ✅ |
| 9 | `rating` | Float | `buyRevwRvgr` | Klover 독자 평점 (10점 만점 기준 부동소수점, 결측 시 `0.0`) | `9.86` | 검증 완료 ✅ |
| 10 | `review_count` | Integer | `buyRevwNumc` | 독자 리뷰/한줄평 수 (결측 시 `0`) | `395` | 검증 완료 ✅ |
| 11 | `isbn` | String | `cmdtCode` | 13자리 표준 도서 식별 번호 (문자열 공백 제거) | `9791158396510` | 검증 완료 ✅ |
| 12 | `category_name` | String | `saleCmdtClstName` | 대분류 카테고리명 (기본값: `컴퓨터/IT`) | `컴퓨터/IT` | 검증 완료 ✅ |
| 13 | `category_code` | String | `saleCmdtClstCode` | 도서 분류 코드 | `33280909` | 검증 완료 ✅ |
| 14 | `inbukCntt` | String | `inbukCntt` | 책 상세 소개 (HTML 태그 정제 및 개행 보존) | `미어캣 2026 최신 기출문제 수록...` | 검증 완료 ✅ |
| 15 | `link` | String | `saleCmdtid` | 도서 상세 페이지 URL 조합 (`https://product.kyobobook.co.kr/detail/{saleCmdtid}`) | `https://product.kyobobook.co.kr/detail/S000213...` | 검증 완료 ✅ |

### 4.2 추가 확장 후보 필드 (⚠️ 검증 필요)
| 필드명 | 데이터 타입 | 대상 출처 | 설명 및 검증 필요 사유 | 상태 |
| :--- | :---: | :--- | :--- | :---: |
| `sub_category` | String | 상세 API 또는 소분류 매핑 테이블 | 세부 카테고리 텍스트(예: `인공지능`, `웹개발`, `데이터베이스` 등).<br>현재 목록 API에서는 8자리 코드(`saleCmdtClstCode`)만 반환되며, 텍스트 명칭을 얻으려면 코드 매핑 딕셔너리 구축 또는 상세 페이지 추가 호출 필요. | **검증 필요 (TODO)** ⚠️ |

---

## 5. 크롤링 안정성 및 예외 처리 규격 (Reliability & Exception Handling)

1. **차단 방지 및 요청 헤더 (Anti-Scraping / WAF 회피)**:
   - 최신 데스크톱 브라우저 환경의 표준 HTTP 요청 헤더를 필수로 전송:
     ```python
     DEFAULT_HEADERS = {
         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
         "Accept": "application/json, text/plain, */*",
         "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
         "Referer": "https://product.kyobobook.co.kr/",
     }
     ```
   - HTTP 연결 재사용을 위한 `requests.Session()` 인스턴스 사용
   - 타임아웃 기본 10초 설정 (`timeout=10`)
2. **요청 지연 시간 (Rate Limiting)**:
   - 교보문고 API 서버 과부하 및 IP 차단을 방지하기 위해 매 페이지 요청 후 **최소 1.0초 이상의 딜레이**를 보장 (기본값: `1.0초`, 설정 가능)
3. **결측치 및 데이터 타입 보정 (Data Cleaning)**:
   - **텍스트 정제**: 도서명, 저자, 출판사 등 텍스트 필드에 포함된 불필요한 HTML 태그(`<mark>`, `<b>` 등)는 정규표현식(`re.sub(r"<[^>]+>", "", text)`)으로 제거
   - **책 소개 개행 보존**: `<br>`, `<p>` 태그는 개행문자(`\n`)로 치환한 뒤 다중 개행 정돈
   - **날짜 정규화**: `YYYYMMDD` 문자열을 `YYYY-MM-DD` 형태로 변환, 유효하지 않은 포맷일 경우 원본 문자열 보존
   - **수치형 결측 방어**: 가격 쉼표(`,`), 공백 등 제거 후 정수(`int`) 변환, 결측 시 기본값 `0` 또는 `0.0` 할당
4. **오류 격리 및 내결함성**:
   - 개별 페이지 수집 중 일시적 네트워크 오류나 HTTP 예외가 발생하더라도 전체 프로세스가 중단되지 않도록 `try-except` 블록으로 격리하고 오류 로그를 기록한 후 다음 페이지를 계속 수집

---

## 6. 개발 환경 및 프로젝트 규칙 (Environment & Project Guidelines)

- **가상환경 및 실행 도구**:
  - 프로젝트 루트의 공통 가상환경(`.venv`) 사용 (새로 생성 금지)
  - 패키지 의존성 관리 및 실행은 `uv` 사용:
    - 패키지 추가: `uv add requests pandas matplotlib koreanize-matplotlib scikit-learn`
    - 스크립트 실행: `uv run python kyobooks/src/scraper.py`
- **디렉터리 구조 및 상대경로 준수**:
  - 워크스페이스 내 파일 경로는 반드시 **상대경로**를 사용합니다.
    - `kyobooks/src/`: 스크래퍼 및 데이터 분석 소스 코드 (`scraper.py`, `eda_analysis.py`, `dashboard.py`)
    - `kyobooks/data/`: 수집 원시 데이터 및 전처리 데이터 파일
    - `kyobooks/images/`: EDA 시각화 차트 이미지 파일
    - `kyobooks/docs/`: 작업 명세서, 가이드라인, EDA 분석 보고서 (`EDA_REPORT.md`)
- **데이터 저장 포맷 및 인코딩 규격**:
  - **CSV 및 JSON 동시 저장 원칙**:
    - CSV: `kyobooks/data/kyobo_it_bestsellers_YYYYMMDD.csv` (Excel 호환 한글 깨짐 방지를 위해 `utf-8-sig` 인코딩 적용)
    - JSON: `kyobooks/data/kyobo_it_bestsellers_YYYYMMDD.json` (`ensure_ascii=False`, `indent=2` 적용)
- **파이썬 코드 작성 규칙**:
  - 모든 `.py` 파일 최상단에는 파일의 목적, 기능, 작성자, 작성일 등을 설명하는 Docstring을 한국어로 필수 작성

---

## 7. 스크립트 인터페이스 사양 (`kyobooks/src/scraper.py`)

- **CLI 파라미터 지원 (`argparse`)**:
  - `--max-pages`: 수집할 최대 페이지 수 지정 (기본값: `None` -> 전수 수집)
  - `--delay`: 페이지 간 요청 대기 시간 (초 단위 부동소수점, 기본값: `1.0`)
  - `--per`: 페이지당 도서 수 (기본값: `20`)
- **실시간 콘솔 진행 현황 로깅**:
  - 수집 시작 시: 총 도서 수, 전체 페이지 수, 수집 대상 페이지 수 출력
  - 페이지별: `[페이지 X/Y] 누적 N권 수집 완료` 실시간 출력
  - 완료 시: 총 수집 건수, 저장된 CSV/JSON 파일 경로 출력

---

## 8. 데이터 분석(EDA) 및 시각화 요구사항 (`kyobooks/src/eda_analysis.py`)

스크래핑을 통해 축적된 데이터를 활용하여 후속 탐색적 데이터 분석(EDA)을 자동으로 수행할 수 있도록 파이프라인을 연계합니다.

### 8.1 5단계 데이터 기본 탐색 및 무결성 검증
1. 상위 5개 행 및 하위 5개 행 표본 추출
2. 데이터 컬럼 및 자료형 정보 확인 (`df.info()`)
3. 전체 행/열 규모 산출 (`df.shape`)
4. 고유 식별자(`isbn`, `link`) 기준 중복 데이터 검증 (`df.duplicated().sum()`)
5. 수치형 및 범주형 기술통계(평균, 사분위수, 왜도, 고유값 빈도 등) 산출

### 8.2 범주형 및 텍스트 특화 분석 (NLP)
- **출판사/저자 분석**: 시장 점유율 상위 20대 출판사 및 최다 저작 등록 상위 저자 집계
- **책 소개(inbukCntt) TF-IDF 키워드 마이닝**: 한국어 2글자 이상 명사/단어 패턴 토큰화 및 불용어 제거를 통한 상위 30대 핵심 기술 키워드 추출 (AI, 클로드, 파이썬, 자격증 등)

### 8.3 12종 시각화 차트 산출 사양 (`kyobooks/images/`)
모든 차트는 `koreanize-matplotlib`을 적용하여 한글 폰트 깨짐을 방지하고 `dpi=300`의 고해상도 PNG로 저장합니다.

| 차트 번호 | 분류 | 파일명 | 분석 내용 및 시각화 유형 |
| :-: | :---: | :--- | :--- |
| 1 | 일변량 | `01_price_distribution.png` | 정가 및 판매가 분포 (히스토그램 & 밀도) |
| 2 | 일변량 | `02_discount_rate_distribution.png` | 할인율 분포 및 구간별 빈도 (박스플롯 & 막대그래프) |
| 3 | 일변량 | `03_rating_distribution.png` | Klover 독자 평점 분포 (0점 제외, 평균/중앙값 표시) |
| 4 | 일변량 | `04_review_count_log_distribution.png` | 독자 리뷰 수 로그 변환 분포 (`log1p`) |
| 5 | 범주형 | `05_top_publishers.png` | IT 베스트셀러 최다 배출 상위 20대 출판사 순위 (수평 막대) |
| 6 | 범주형 | `06_top_authors.png` | IT 베스트셀러 최다 등록 상위 20대 저자/역자 순위 (수평 막대) |
| 7 | 텍스트 | `07_tfidf_keywords_top30.png` | 책 소개 기반 TF-IDF 상위 30대 핵심 기술 키워드 가중치 |
| 8 | 이변량 | `08_pub_price_vs_rating.png` | 상위 15대 출판사별 평균 판매가 및 독자 평점 이중 축 비교 |
| 9 | 이변량 | `09_scatter_price_vs_rating.png` | 도서 판매가 vs 평점 상관 산점도 및 선형 회귀 추세선 (버블: 리뷰수) |
| 10 | 시계열 | `10_publication_year_trend.png` | 출간 연도별 베스트셀러 점유 추이 (2020년 이후 꺾은선) |
| 11 | 다변량 | `11_correlation_heatmap.png` | 주요 수치형 변수(순위, 가격, 평점, 리뷰 등) 피어슨 상관계수 히트맵 |
| 12 | 다변량 | `12_tier_price_and_rating.png` | 순위 구간(1~50위, 51~100위 등 Tier)별 가격 및 평점 특성 비교 (박스플롯) |

### 8.4 분석 리포트 연계
- 분석 결과는 마크다운 문서 `kyobooks/docs/EDA_REPORT.md`로 정리하여 비즈니스/출판 전략적 인사이트를 제공합니다.

---

## 9. 미검증 항목 및 향후 검증(TODO) 체크리스트

| 항목 | 구분 | 내용 | 권장 조치 사항 |
| :--- | :---: | :--- | :--- |
| 세부 카테고리명 (`sub_category`) | 데이터 필드 | 개별 도서의 텍스트 소분류(예: '웹개발', '인공지능')가 목록 API 응답에 직접 포함되지 않음 | 1) `saleCmdtClstCode` 분류 코드 테이블 확보 또는<br>2) 상세 페이지 API 검증 후 단계적 보완 |
| 도서 상세 API 주소 | API 엔드포인트 | 상세 페이지용 REST API (`/api/gw/pub/pdt/detail/{id}`) 엔드포인트의 헤더/쿠키 요구사항 및 쿼터 제한 미확인 | 프로토타입 호출을 통한 유효성 및 응답 스키마 확인 필수 |
| 브라우저 자동화 (Selenium/Playwright) | 대체 수집 방식 | 초기 백업 기획에 포함되었으나 현재 REST API가 정상 동작하므로 기본 파이프라인에서 제외됨 | API 엔드포인트 WAF 정책 변경이나 캡차(CAPTCHA) 도입 시 예비 대안으로 유지 |
| 데이터 파일명 단일화 (`it_books_raw` vs 날짜별) | 파일 명명 | 백업본의 고정 파일명(`it_books_raw.csv`)과 최신본의 일자별 파일명(`kyobo_it_bestsellers_YYYYMMDD.csv`) | 스냅샷 히스토리 관리를 위해 **일자별 파일명을 표준**으로 채택, 필요시 심볼릭 링크 또는 최신 복사본 유지 |
