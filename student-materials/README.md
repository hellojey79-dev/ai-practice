# 🎓 교보문고 IT 베스트셀러 데이터 엔지니어링 & 시니어 EDA 실습 패키지 (Student Materials)

본 저장소는 교보문고 IT/컴퓨터 분야 베스트셀러 데이터를 활용하여 **데이터 수집(Web Scraping)부터 데이터 정제, 5단계 탐색적 데이터 분석(EDA), 12종 고해상도 시각화, 인터랙티브 웹 대시보드 구축까지** 데이터 파이프라인의 전 과정을 직접 실습할 수 있도록 제작된 **교육생 배포용 패키지**입니다.

---

## 📁 폴더 구조 (Project Structure)

표준 하네스 데이터 파이프라인 규격(4대 표준 폴더 구조)을 준수합니다:

```text
student-materials/
├── README.md                  # 교육생 패키지 시작 안내서 (본 문서)
├── requirements.txt           # 필수 파이썬 패키지 의존성 목록
├── data/                      # 실습용 데이터셋 저장소
│   ├── sample_kyobo_bestsellers.csv   # 상위 100권 실습용 샘플 데이터 (CSV)
│   └── sample_kyobo_bestsellers.json  # 상위 100권 실습용 샘플 데이터 (JSON)
├── docs/                      # 실습 문서 및 가이드라인
│   ├── HANDS_ON_GUIDE.md      # 초보자 친화적 단계별 상세 실습 가이드
│   └── DATA_SCHEMA.md         # 15개 수집 필드 명세 및 6대 메타 스키마 매핑
├── images/                    # 시각화 결과 차트 자동 저장소 (DPI 300)
│   ├── 01_price_distribution.png ~ 12_rank_tier_comparison.png (12종 차트)
└── src/                       # 단계별 파이썬 실습 코드
    ├── 01_scraper.py          # [Step 1] REST API 기반 도서 데이터 수집
    ├── 02_clean_and_eda.py    # [Step 2] 데이터 정제 및 5단계 EDA 분석 (TF-IDF 포함)
    ├── 03_visualization.py    # [Step 3] 12종 고해상도 시각화 차트 생성
    └── 04_dashboard.py        # [Step 4] Streamlit 인터랙티브 웹 대시보드 실행
```

---

## 🚀 빠른 시작 가이드 (Quick Start)

### Step 0. 환경설정 및 패키지 설치
Python 3.10 이상 환경에서 빠른 패키지 관리자 `uv` 또는 `pip`을 사용하여 필요한 라이브러리를 설치합니다.

```bash
# uv 사용 시 (권장)
uv pip install -r student-materials/requirements.txt

# 일반 pip 사용 시
pip install -r student-materials/requirements.txt
```

---

### Step 1. 데이터 수집 실습 (`01_scraper.py`)
교보문고 공식 REST API 게이트웨이를 호출하여 IT/컴퓨터 베스트셀러 도서 목록을 수집합니다.

```bash
# 기본 실행: 상위 5페이지(100권) 실습 수집
uv run python student-materials/src/01_scraper.py --max-pages 5

# 옵션: 전수 수집 (약 600~700권 전체)
uv run python student-materials/src/01_scraper.py --max-pages 0
```
> **Tip**: 네트워크 환경이 여의치 않은 경우에도 `data/sample_kyobo_bestsellers.csv`가 기본 제공되므로 곧바로 다음 단계 실습이 가능합니다.

---

### Step 2. 데이터 정제 및 5단계 EDA 분석 (`02_clean_and_eda.py`)
20년차 시니어 데이터 분석가의 방법론에 따라 데이터의 무결성을 검증하고 기술통계 및 TF-IDF 키워드를 추출합니다.

```bash
# 기본 실행 (최신 수집 데이터 또는 샘플 데이터 자동 로드)
uv run python student-materials/src/02_clean_and_eda.py
```
- **주요 검증 항목**: 상하위 5개 행 표본, 결측치 현황(info), 데이터 볼륨(shape), 중복 검사, 수치/범주 기술통계, 책 소개 TF-IDF 상위 30대 키워드.

---

### Step 3. 12종 고해상도 시각화 차트 생성 (`03_visualization.py`)
한글 깨짐 없는 12가지 통계 시각화 차트를 일괄 생성하여 `images/` 폴더에 저장합니다.

```bash
uv run python student-materials/src/03_visualization.py
```
- **생성 차트**: 가격 분포, 할인율, 평점 분포, 리뷰 수 로그 변환, 상위 20대 출판사/저자, TF-IDF 핵심 키워드, 출판사별 가격 vs 평점, 가격-평점 산점도 및 추세선, 출간연도별 추이, 피어슨 상관 히트맵, 순위 구간(Tier)별 비교.

---

### Step 4. 인터랙티브 웹 대시보드 실행 (`04_dashboard.py`)
Streamlit과 Plotly를 활용하여 로컬 브라우저에서 대시보드를 구동합니다.

```bash
uv run streamlit run student-materials/src/04_dashboard.py
```
- 브라우저 주소(`http://localhost:8501`)로 접속하여 실시간 도서 검색, 가격 슬라이더 필터링, 출판사 성과 드릴다운, 반응형 차트를 직접 조작해 보세요.

---

## 📚 상세 실습 문서 링크
- 📖 [초보자를 위한 상세 실습 가이드](docs/HANDS_ON_GUIDE.md)
- 📋 [데이터 스키마 및 범용 메타 매핑 명세서](docs/DATA_SCHEMA.md)

---

## 🔒 보안 및 라이선스 안내
- 본 실습 패키지는 교육 및 연구 목적으로만 제공됩니다.
- 본 패키지에는 어떠한 개인정보, API 비밀키, 인증 토큰도 포함되어 있지 않습니다.
