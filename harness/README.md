# 🧪 데이터 크롤링 · 시니어 EDA · 웹 대시보드 하네스 (Harness)

본 디렉터리는 어떠한 새로운 사이트라도 신속하게 크롤링하고, 20년차 시니어 데이터 분석가 방법론에 따라 심층 탐색적 데이터 분석(EDA), 12종 시각화, 통계표, 종합 리포트 및 Chart.js Bento 대시보드까지 원스톱으로 구축할 수 있도록 설계된 **실행 하네스(Execution Harness)**입니다.

---

## 📁 하네스 폴더 구조

```text
harness/
├── data/                       # 수집된 원본 및 정제 데이터셋 (.csv, .json)
├── docs/                       # 하네스 아키텍처 및 분석 산출물 문서
│   ├── pipeline_plan.md        # [아티팩트] 파이프라인 구현 계획서
│   ├── pipeline_workflow.md    # [아티팩트] 단계별 실행 매뉴얼 & 17개 체크리스트
│   └── pipeline_standards.md   # [아티팩트] 엔지니어링 표준 원칙
├── images/                     # 생성된 12종 고해상도 시각화 차트 이미지
└── src/                        # 핵심 실행 스크립트 및 템플릿
    ├── scraper_template.py     # 하이브리드 웹 크롤러 표준 템플릿
    ├── validate_dataset.py     # 데이터 무결성 검증 품질 게이트 훅
    ├── eda_template.py         # 20년차 시니어 EDA & 12종 차트 생성기
    ├── export_web_template.py  # 대시보드용 data.js 번들러
    ├── serve_webapp.py         # 로컬 웹 대시보드 HTTP 서버 실행기
    └── webapp/                 # Bento Grid 다크 모드 Chart.js 웹앱
        ├── index.html          # 대시보드 마크업
        ├── dashboard.js        # 차트 & 필터링 로직
        └── styles.css          # 커스텀 스타일
```

---

## 🚀 새로운 사이트 분석 시 4단계 퀵스타트

### Step 1: 데이터 수집 (크롤링)
`harness/src/scraper_template.py`를 타깃 사이트 엔드포인트/셀렉터에 맞춰 수정한 후 실행합니다:
```bash
uv run python harness/src/scraper_template.py --output-dir harness/data --prefix new_site
```

### Step 2: 무결성 검증 훅 실행
```bash
uv run python harness/src/validate_dataset.py --file harness/data/new_site_YYYYMMDD.csv
```

### Step 3: 시니어 EDA & 차트 생성
```bash
uv run python harness/src/eda_template.py --data-path harness/data/new_site_YYYYMMDD.csv --output-images harness/images
```

### Step 4: 대시보드 번들링 & 로컬 실행
```bash
uv run python harness/src/export_web_template.py --data-path harness/data/new_site_YYYYMMDD.csv --out-js harness/src/webapp/data.js
uv run python harness/src/serve_webapp.py
```
- 브라우저에서 `http://localhost:8080` 접속하여 대시보드 확인
