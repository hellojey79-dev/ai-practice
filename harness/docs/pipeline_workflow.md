# 🔄 [하네스 워크플로우] 범용 데이터 크롤링 · EDA · 대시보드 엔드투엔드 실행 매뉴얼

본 문서는 새로운 웹사이트가 주어졌을 때 데이터 수집부터 최종 웹 대시보드 배포까지 한 치의 오차 없이 실행할 수 있도록 정의된 표준 운영 절차(SOP)입니다.

---

## 1. 단계별 실행 절차 (Step-by-Step SOP)

### 📌 Step 1: 타깃 사이트 분석 및 크롤러 구성
1. **타깃 탐색**: 브라우저 DevTools의 `Network` 탭(Fetch/XHR)을 분석하여 내부 API 엔드포인트가 존재하는지 먼저 확인합니다.
   - API가 존재할 경우: `requests`/`httpx`로 직접 JSON 엔드포인트 호출 (가장 빠르고 안정적)
   - API가 없을 경우: `BeautifulSoup` 및 정규식 기반 HTML 파싱 적용
   - 동적 렌더링(SPA)일 경우: `Playwright` 헤드리스 브라우저 적용
2. **스크립트 생성**: `harness/src/scraper_template.py`를 기반으로 타깃 파서 구현
3. **실행 및 저장**:
   ```bash
   uv run python harness/src/scraper_template.py
   ```
   - 산출물: `harness/data/<site>_<topic>_YYYYMMDD.csv` 및 `.json`

---

### 📌 Step 2: 데이터 무결성 검증 훅 실행
1. 데이터셋 생성 즉시 무결성 검증 훅을 실행하여 정합성을 확인합니다:
   ```bash
   uv run python harness/src/validate_dataset.py --file harness/data/<파일명>.csv
   ```
2. **검증 기준**:
   - [x] 최소 행 수 50건 이상 확보
   - [x] 중복 레코드 수 0건 (또는 0.5% 미만)
   - [x] 주요 수치형 변수(가격, 평점, 수량 등)의 결측률 0.0% 확인

---

### 📌 Step 3: 20년차 시니어 EDA 파이프라인 가동
1. **분석 스크립트 실행**:
   ```bash
   uv run python harness/src/eda_template.py --data-path harness/data/<파일명>.csv
   ```
2. **수행 내역**:
   - 5단계 기본 탐색(`head(5)`, `tail(5)`, `info()`, `shape`, `duplicated()`, `describe()`)
   - 범주형 상위 20~30대 빈도 분석
   - 텍스트 TF-IDF 상위 30대 키워드 가중치 추출 (형태소 분석기 미사용)
   - 12종 시각화 차트 생성 및 `harness/images/`에 PNG 저장 (한글 폰트 적용, Seaborn 전역 스타일 금지)
   - 10종 통계표 및 피봇테이블 산출

---

### 📌 Step 4: 종합 심층 분석 리포트 작성
1. 분석 결과를 `harness/docs/EDA_REPORT.md` 파일로 작성합니다.
2. **필수 포함 사항**:
   - 데이터 기본 구조 및 결측치 현황 표
   - 12종 시각화 차트 이미지 삽입 및 **각 차트마다 수반 통계표 배치**
   - **모든 시각화 차트에 대해 20년차 시니어 관점의 300자 이상 통계적 해석 코멘트 필수 작성**
   - 도메인 비즈니스 전략 제언 4대 로드맵 도출

---

### 📌 Step 5: Chart.js Bento 웹 대시보드 빌드 및 구동
1. **데이터 번들링**:
   ```bash
   uv run python harness/src/export_web_template.py --data-path harness/data/<파일명>.csv
   ```
   - `harness/src/webapp/data.js`로 번들 생성 (로컬 더블클릭 실행 지원)
2. **로컬 서버 구동 및 검증**:
   ```bash
   uv run python harness/src/serve_webapp.py
   ```
   - Bento Grid 모던 다크 테마, 5대 KPI 카드, Chart.js 7종 차트, 실시간 필터 및 CSV 다운로드 정상 동작 확인

---

## 2. 17개 사후 품질 검증 체크리스트

| 번호 | 체크 항목 | 검증 기준 |
|:---:|:---|:---|
| 1 | 전문 분석가 톤 & 한국어 | 모든 주석, 리포트 텍스트, 차트 레이블이 한국어로 작성되었는가? |
| 2 | uv 가상환경 원칙 | 루트의 단일 `.venv`를 재사용하고 `uv run python`으로 실행했는가? |
| 3 | Seaborn 전역 스타일 금지 | `sns.set_theme()` 등을 사용하지 않고 순수 Matplotlib 스타일을 유지했는가? |
| 4 | 한글 폰트 적용 | `koreanize-matplotlib`를 import하여 한글 깨짐이 없는가? |
| 5 | 상위/하위 5개 행 출력 | `head(5)` 및 `tail(5)` 표본이 명시되었는가? |
| 6 | info() 기본 정보 제시 | 컬럼별 데이터 타입 및 결측치 현황이 명시되었는가? |
| 7 | 행과 열의 규모 확인 | `shape`가 명확히 보고서에 기록되었는가? |
| 8 | 중복 데이터 전수 검증 | 중복 데이터 건수가 확인되었는가? |
| 9 | 수치형 & 범주형 기술통계 | `describe()` 요약 통계가 완벽히 산출되었는가? |
| 10 | 범주형 상위 빈도 분석 | 항목이 많을 때 상위 20~30개로 한정하여 시각화했는가? |
| 11 | TF-IDF 키워드 분석 | 형태소 분석 없이 TF-IDF로 상위 30 키워드를 추출·표·차트화했는가? |
| 12 | images 폴더 분리 저장 | 시각화 차트가 `images/`에 PNG로 개별 저장되었는가? |
| 13 | 10종 이상의 다양한 시각화 | 일변량, 이변량, 다변량 최소 10종(권장 12종)이 생성되었는가? |
| 14 | 시각화별 표 동반 | 모든 차트에 피봇테이블이나 교차표가 수반되었는가? |
| 15 | 시각화별 300자 이상 해석 | 각 차트마다 300자 이상의 통계적 해석이 작성되었는가? |
| 16 | 단일 통합 리포트 작성 | 하나의 마크다운 리포트로 체계화되었는가? |
| 17 | 대시보드 독립 실행 보장 | `data.js`를 통해 로컬 파일로 열어도 CORS 오류 없이 실행되는가? |
