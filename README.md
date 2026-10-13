# 📚 교보문고 IT/컴퓨터 베스트셀러 심층 분석 & 웹 대시보드

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Demo-2ea44f?style=for-the-badge&logo=github)](https://hellojey79-dev.github.io/ai-practice/)
[![Chart.js](https://img.shields.io/badge/Chart.js-v4.4.1-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v3-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![uv](https://img.shields.io/badge/Package_Manager-uv-DE5FE9?style=for-the-badge)](https://github.com/astral-sh/uv)

국내 대표 도서 유통 채널인 교보문고의 **IT/컴퓨터 분야 베스트셀러 678권 전수 데이터**를 수집·정제하고, 20년차 시니어 데이터 분석가의 방법론에 따라 심층 탐색적 데이터 분석(EDA)과 **Chart.js 기반 Bento Grid 모던 다크 웹 대시보드**를 구축한 프로젝트입니다.

---

## 🌐 라이브 웹 대시보드 바로가기

별도의 설치나 서버 구동 없이 아래 링크를 클릭하시면 웹 브라우저에서 즉시 인터랙티브 대시보드를 체험하실 수 있습니다:

👉 **[https://hellojey79-dev.github.io/ai-practice/](https://hellojey79-dev.github.io/ai-practice/)**

---

## ✨ 대시보드 주요 기능

1. **Bento Grid 모던 다크 UI**
   - Slate 900 기반 글래스모피즘(Glassmorphism)과 네온 액센트 디자인 적용
   - PC, 태블릿, 모바일을 완벽히 지원하는 반응형 레이아웃
2. **다차원 실시간 글로벌 필터**
   - **출판사 선택**: 한빛미디어, 길벗, 영진닷컴, 골든래빗 등 상위 출판사별 필터링
   - **가격대 칩**: 2만원 이하, 2만~3만원, 3만~4만원, 4만원 초과
   - **할인율 정책**: 10% 정률할인(상업 단행본) vs 0% 무할인(대학교재/공식수험서)
   - **출간 시기**: 2026년 당해 신간, 2025년, 2024년 이전
   - **실시간 검색**: 도서명 및 저자명 250ms 디바운스 실시간 검색 지원
3. **5대 핵심 KPI 요약 카드**
   - 총 분석 도서 수 (필터 적용에 따라 실시간 비중 연산)
   - 평균 판매가 및 가격 중앙값
   - 독자 평균 평점 및 10점 만점 도서 수/비율
   - 평균 리뷰 수 및 총 누적/최다 리뷰 수
   - 2026년 신간 점유율
4. **Chart.js v4 인터랙티브 시각화 차트 (7종)**
   - **Chart 1 (Bar)**: 도서 판매가 5천원 단위 구간별 분포
   - **Chart 2 (Horizontal Bar)**: 상위 8대 출판사 베스트셀러 진입 점유율
   - **Chart 3 (Doughnut)**: 할인율 정책 점유율 (10% 할인 vs 0% 무할인)
   - **Chart 4 (Line & Area)**: 출간 연도별 신간 점유 추이 (2020~2026)
   - **Chart 5 (Scatter/Bubble)**: 판매가 vs 평점 상관관계 (버블 크기: 리뷰 수)
   - **Chart 6 (Dual Axis Bar)**: 순위 Tier별 평균 판매가 및 리뷰 수 비교
   - **Chart 7 (Horizontal Bar)**: 책 소개 TF-IDF 상위 12대 핵심 기술 키워드
5. **도서 목록 탐색기 (데이터 테이블)**
   - 순위, 판매가, 평점, 리뷰 수 컬럼별 **양방향 정렬**
   - 페이지당 10 / 15 / 25 / 50개 보기 페이지네이션
   - 필터링된 결과 데이터의 **UTF-8 BOM CSV 파일 다운로드**
   - 개별 도서 교보문고 공식 상품 페이지 바로가기 연동

---

## 📁 프로젝트 디렉터리 구조

```text
ai-practice/
├── .agents/                    # 특화 스킬 및 규칙 가이드
│   └── skills/
│       ├── py-eda/             # 20년차 시니어 데이터 분석가 EDA 스킬
│       └── marp-slides/        # Marp 프레젠테이션 제작 스킬
├── kyobooks/                   # 교보문고 IT 베스트셀러 프로젝트
│   ├── data/                   # 수집된 원본 데이터셋 (CSV, JSON)
│   │   ├── kyobo_it_bestsellers_20261013.csv
│   │   └── kyobo_it_bestsellers_20261013.json
│   ├── docs/                   # 심층 EDA 리포트 문서
│   │   └── EDA_REPORT.md       # 12종 시각화 및 통계표 포함 종합 분석 보고서
│   ├── images/                 # 고해상도 EDA 시각화 차트 이미지 (12종)
│   └── src/                    # 소스 코드
│       ├── eda_analysis.py     # 5단계 탐색 및 12종 시각화 파이썬 파이프라인
│       ├── export_data_for_web.py # data.js 웹 번들러 스크립트
│       ├── serve_webapp.py     # 로컬 정적 HTTP 서버 실행기
│       └── webapp/             # 웹 대시보드 프론트엔드
│           ├── index.html      # Bento Grid 메인 마크업
│           ├── dashboard.js    # Chart.js 시각화 & 필터링 로직
│           ├── styles.css      # 다크 테마 커스텀 스타일
│           └── data.js         # 독립 실행용 번들 데이터셋
└── README.md                   # 프로젝트 안내 문서 (본 파일)
```

---

## 🚀 로컬 실행 방법

### 방법 1: 파이썬 로컬 서버 실행 (권장)
가상환경(`uv`)을 통해 로컬 서버를 실행하면 기본 웹 브라우저가 자동으로 열립니다:
```bash
uv run python kyobooks/src/serve_webapp.py
```
- 기본 접속 주소: `http://localhost:8080`

### 방법 2: 브라우저 단독 실행
별도의 웹서버나 파이썬 실행 없이도 `kyobooks/src/webapp/index.html` 파일을 파일 탐색기에서 더블클릭하면 브라우저에서 즉시 대시보드가 정상 구동됩니다 (CORS 이슈 없는 독립형 번들 탑재).

---

## 📊 관련 분석 보고서

- **[교보문고 IT/컴퓨터 베스트셀러 심층 EDA 분석 보고서](kyobooks/docs/EDA_REPORT.md)**:
  - 678권 전수 데이터에 대한 5단계 무결성 검증
  - 도서정가제 하의 가격대별 스위트 스팟(2만 4천원 ~ 2만 8천원) 규명
  - 출판사별 과점 점유 구조와 골든래빗 등 강소 출판사 효율성 분석
  - 12종 시각화 차트별 300자 이상의 통계적 해석 및 2026 IT 출판 4대 비즈니스 제언
