# 🚀 AI Practice: 국내 도서 유통 채널(교보문고 · YES24) IT 베스트셀러 데이터 분석 & 웹 대시보드

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Demo-2ea44f?style=for-the-badge&logo=github)](https://hellojey79-dev.github.io/ai-practice/)
[![Chart.js](https://img.shields.io/badge/Chart.js-v4.4.1-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v3-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![uv](https://img.shields.io/badge/Package_Manager-uv-DE5FE9?style=for-the-badge)](https://github.com/astral-sh/uv)

본 저장소는 국내 양대 도서 유통 채널인 **교보문고**와 **YES24**의 IT/컴퓨터 베스트셀러 전수 데이터를 수집·가공하고, 20년차 시니어 데이터 분석가 방법론에 입각한 **탐색적 데이터 분석(EDA)**, **Chart.js 기반 인터랙티브 웹 대시보드**, **Marp 슬라이드 및 PPTX 발표자료**, 그리고 **에이전트 엔지니어링 스킬셋**을 통합 구축한 종합 데이터 프로젝트 저장소입니다.

---

## 🌐 교보문고 IT 베스트셀러 웹 대시보드 (라이브 배포)

별도의 프로그램 설치나 서버 실행 없이, 아래 링크를 통해 브라우저에서 전수 수집 678권 데이터에 대한 실시간 인터랙티브 시각화 대시보드를 즉시 이용하실 수 있습니다:

### 👉 **웹앱 접속 주소**: [https://hellojey79-dev.github.io/ai-practice/](https://hellojey79-dev.github.io/ai-practice/)

- **테마 & 레이아웃**: Slate 900 기반 **Bento Grid 모던 다크 테마**
- **실시간 다차원 필터**: 출판사(한빛미디어, 길벗 등), 가격대 칩, 할인율(10% vs 0%), 출간 시기(2026 신간 등), 도서명/저자 실시간 검색
- **핵심 KPI 카드**: 총 도서 수, 평균 판매가, 독자 평균 평점, 평균 리뷰 수, 2026년 신간 점유율
- **Chart.js 7종 시각화**: 가격대 분포(Bar), 출판사 점유율(H-Bar), 할인율 정책(Doughnut), 연도별 추이(Line/Area), 평점-판매가 산점도(Bubble), 순위 Tier 비교(Dual-Axis), TF-IDF 키워드 Top 12
- **도서 목록 탐색기**: 양방향 컬럼 정렬, 페이지네이션, 교보문고 공식 링크 연동, **필터링 데이터 CSV 다운로드**

---

## 📂 전체 저장소 구조 (Repository Architecture)

```text
ai-practice/
├── .agents/                    # 🤖 전문 AI 에이전트 커스텀 스킬 및 규칙
│   └── skills/
│       ├── py-eda/             # 20년차 시니어 데이터 분석가 EDA 표준 파이프라인 스킬
│       └── marp-slides/        # Marp 기반 고품질 프레젠테이션 제작 스킬
│
├── kyobooks/                   # 📖 교보문고 IT 베스트셀러 프로젝트
│   ├── data/                   # 전수 수집 데이터셋 (CSV, JSON)
│   │   ├── kyobo_it_bestsellers_20261013.csv  (678권 전수 데이터)
│   │   └── kyobo_it_bestsellers_20261013.json
│   ├── docs/                   # 정밀 EDA 리포트 및 프롬프트
│   │   └── EDA_REPORT.md       # 12종 시각화 & 세부 통계표 포함 종합 분석 리포트
│   ├── images/                 # 고해상도 시각화 차트 이미지 (12종)
│   └── src/                    # 파이썬 파이프라인 및 웹 프론트엔드
│       ├── eda_analysis.py     # 5단계 무결성 검증 및 12종 시각화 생성 파이프라인
│       ├── export_data_for_web.py # webapp/data.js 번들러 스크립트
│       ├── serve_webapp.py     # 로컬 정적 HTTP 서버 구동 스크립트
│       └── webapp/             # Chart.js 웹앱 프론트엔드
│           ├── index.html      # Bento Grid 다크 대시보드 마크업
│           ├── dashboard.js    # Chart.js 7종 차트 & 필터링 상태 엔진
│           ├── styles.css      # 다크 테마 커스텀 스타일
│           └── data.js         # 독립 실행용 전수 데이터 번들
│
├── yes24/                      # 📗 YES24 IT/테크 베스트셀러 프로젝트
│   ├── data/                   # YES24 베스트셀러 원본 및 정제 데이터셋
│   ├── docs/                   # 분석 리포트, 발표자료, 엑셀 대시보드
│   │   ├── eda_report.md       # YES24 종합 EDA 분석 보고서
│   │   ├── eda_report.docx     # 보고서 워드 문서 (.docx)
│   │   ├── eda_slides.md       # Marp 프레젠테이션 발표 슬라이드 마크다운
│   │   ├── eda_slides.html     # HTML 렌더링 발표 슬라이드
│   │   ├── eda_presentation.pptx # 공식 발표 파워포인트 (.pptx)
│   │   └── yes24_eda_dashboard.xlsx # 피봇 & 차트 포함 엑셀 대시보드
│   ├── images/                 # YES24 분석 시각화 이미지 산출물
│   └── src/                    # YES24 데이터 수집 및 분석 스크립트
│
├── .gitignore                  # Git 추적 제외 규칙 (숨김폴더 제외 및 py-eda, marp-slides 예외)
└── README.md                   # 전체 저장소 통합 안내 문서 (본 파일)
```

---

## 🛠️ 서브 프로젝트별 상세 안내

### 1. 교보문고 IT 베스트셀러 심층 분석 & 웹 대시보드 (`kyobooks/`)
- **데이터 규모**: 2026년 10월 13일 기준 IT/컴퓨터 베스트셀러 **678권 전수 수집** (결측률 0.00% 완전 데이터)
- **주요 통계 요약**:
  - **평균 판매가**: 25,854원 (베스트셀러의 49.4%가 2만~3만원대 구간에 밀집)
  - **할인율 정책**: 82.6%가 도서정가제 법정 최대치인 10% 정률 할인 적용
  - **독자 평점 & 리뷰**: 유효 평점 평균 9.60점(75.8%가 9.5점 이상 상향 편향), 최상위권(1~50위) 평균 리뷰 수는 47.06개로 하위권 대비 약 3.8배
  - **시장 점유율**: 한빛미디어(112권, 16.5%), 길벗(57권, 8.4%)의 과점 체제 속 골든래빗(28권, 평균 평점 9.88, 평균 순위 217위) 등 강소 출판사의 약진
  - **TF-IDF 핵심 키워드**: `ai`(66.45), `데이터`(41.68), `실전`(28.16), `실무`(27.20), `업무`(21.01)
  - **기술 수명 주기**: 최근 3개년(2024~2026) 신간이 전체의 72.57%를 차지
- **상세 보고서**: [kyobooks/docs/EDA_REPORT.md](kyobooks/docs/EDA_REPORT.md)

### 2. YES24 IT/테크 베스트셀러 분석 & 발표 프레젠테이션 (`yes24/`)
- **분석 보고서**: [yes24/docs/eda_report.md](yes24/docs/eda_report.md) 및 Word 문서([yes24/docs/eda_report.docx](yes24/docs/eda_report.docx))
- **Marp 발표 슬라이드**: [yes24/docs/eda_slides.html](yes24/docs/eda_slides.html) 및 Markdown([yes24/docs/eda_slides.md](yes24/docs/eda_slides.md))
- **파워포인트 덱**: [yes24/docs/eda_presentation.pptx](yes24/docs/eda_presentation.pptx)
- **엑셀 분석 대시보드**: [yes24/docs/yes24_eda_dashboard.xlsx](yes24/docs/yes24_eda_dashboard.xlsx)

### 3. AI 에이전트 엔지니어링 커스텀 스킬 (`.agents/skills/`)
- **`py-eda`**: 20년차 시니어 분석가 페르소나 기반 데이터 기본 탐색 5단계, Seaborn 전역 스타일 제한, 한글 폰트 적용, TF-IDF 키워드 추출, 12종 시각화 및 표 동반 표준 가이드
- **`marp-slides`**: 가독성과 전문성이 검증된 Marp 기반 프레젠테이션 슬라이드 자동 생성 가이드

---

## 💻 로컬 개발 환경 및 실행 가이드

### 환경 요구사항
- **Python**: 3.12 이상
- **패키지 관리자**: `uv` (워크스페이스 루트의 단일 `.venv` 가상환경 재사용)

### 교보문고 웹 대시보드 로컬 실행

#### 1) 로컬 웹서버 실행 (권장)
```bash
uv run python kyobooks/src/serve_webapp.py
```
- 기본 포트 `8080`으로 정적 서버가 시작되며 기본 웹 브라우저가 자동으로 실행됩니다.
- 포트 변경 시: `uv run python kyobooks/src/serve_webapp.py --port 9000`

#### 2) 브라우저 단독 실행
별도의 터미널 명령어 없이도 `kyobooks/src/webapp/index.html` 파일을 파일 탐색기에서 더블클릭하면 즉시 대시보드가 정상 작동합니다 (독립형 JS 번들러가 탑재되어 CORS 이슈가 발생하지 않습니다).

#### 3) EDA 파이프라인 재실행
```bash
uv run python kyobooks/src/eda_analysis.py --data-path kyobooks/data/kyobo_it_bestsellers_20261013.csv
```
- 12종 시각화 이미지 재생성(`kyobooks/images/`) 및 통계표 산출

#### 4) 최신 데이터 웹 번들링
```bash
uv run python kyobooks/src/export_data_for_web.py
```
- 최신 CSV 데이터를 웹 대시보드용 `kyobooks/src/webapp/data.js` 파일로 재생성

---

## 📜 라이선스 및 저작권
본 프로젝트의 소스 코드는 학습 및 비상업적 분석 연구 목적으로 관리됩니다. 수집된 도서 메타데이터의 저작권은 각 원 저작권자 및 유통 채널(교보문고, YES24)에 있습니다.
