---
name: marp-slides
description: Marp 마크다운 슬라이드, 프레젠테이션 덱, 발표 자료, EDA 슬라이드 작성 시 반드시 사용하는 전문 프레젠테이션 제작 스킬입니다. 사용자가 Marp, 슬라이드, 발표 자료, 프레젠테이션, 덱, 슬라이드쇼, 강의안, 보고서 슬라이드 변환 등을 요청할 때 항상 이 스킬을 사용하세요.
---

# 📽️ marp-slides: 전문 Marp 프레젠테이션 덱 제작 가이드

본 스킬은 EDA(탐색적 데이터 분석) 보고서, 기술 기획서, 비즈니스 리포트를 기반으로 **Marp(Markdown Presentation Ecosystem)** 엔진에 최적화된 고품질, 대규모(30페이지 내외) 프레젠테이션 슬라이드 덱을 작성할 때 적용합니다.

---

## 1. 핵심 설계 원칙 및 기본 제약

1. **상단 헤더(Header) 및 하단 푸터(Footer) 완전 배제**:
   - `header`, `footer` 메타데이터 속성을 일절 사용하지 않습니다. 슬라이드 상·하단에 고정 텍스트가 노출되어 콘텐츠 가독성을 저해하는 것을 방지합니다.
2. **슬라이드 번호 및 시각화 번호 완전 배제**:
   - `paginate: false`로 설정하여 슬라이드 하단에 페이지 번호가 노출되지 않도록 합니다.
   - 슬라이드 제목, 표 제목, 본문 어디에도 `1.`, `Slide 1`, `[차트 01]`, `차트 1.` 같은 번호를 일절 붙이지 않고, 순수 주제명(예: `베스트셀러 도서 판매가 분포`, `수치형 변수 상관계수 행렬 히트맵`)으로만 작성합니다.
3. **그래프 시각화 이미지 중심 레이아웃**:
   - HTML `<img>` 태그 대신 표준 마크다운 이미지 문법(`![대체텍스트](../images/파일명.png)`)을 사용합니다.
   - 글로벌 스타일에 `max-height: 390px`, `object-fit: contain`, 부드러운 그림자(`box-shadow`)와 중앙 정렬을 적용하여 차트가 슬라이드 정중앙에 선명하게 부각되도록 합니다.
4. **흐름을 잡아주는 파트별 섹션 간지(Divider Slide) 필수 삽입**:
   - 대주제가 전환될 때마다 시각적 환기를 주는 다크 그라데이션 간지 슬라이드를 배치합니다 (`PART 1. 분석 개요 및 데이터 무결성`, `PART 2. 핵심 변수 일변량 심층 분석` 등).
5. **전 슬라이드 2분 분량 발표자 노트(Presenter Notes) 필수 수록**:
   - Marp 발표자 뷰(`Presenter View`)와 100% 호환되는 마크다운 주석(`<!-- [발표자 노트 | 약 2분 분량] ... -->`)을 모든 슬라이드 하단에 작성합니다.
   - 단순 요약이 아닌, **실제 발표자가 2분 동안 여유롭고 전문성 있게 낭독할 수 있는 450~600자 분량의 정교한 구어체 발표 대본**이어야 합니다.
6. **언어 및 경로 원칙**:
   - 모든 슬라이드 텍스트, 코드 주석, 발표자 노트는 **한국어로만 작성**합니다.
   - 워크스페이스 내 파일 참조는 철저히 **상대경로**(`../images/...`, `yes24/docs/...`)를 사용합니다.

---

## 2. 표준 Marp 프론트매터 및 글로벌 스타일 가이드

모든 Marp 슬라이드 문서는 최상단에 다음 YAML 프론트매터와 CSS 스타일 블록을 기본 탑재합니다:

```yaml
---
marp: true
theme: default
paginate: false
style: |
  section {
    font-family: 'Pretendard', 'Malgun Gothic', 'Noto Sans KR', sans-serif;
    font-size: 19px;
    line-height: 1.5;
    padding: 35px 50px;
    color: #1e293b;
    background-color: #ffffff;
  }
  h1 {
    font-size: 30px;
    color: #0f172a;
    border-bottom: 3px solid #2563eb;
    padding-bottom: 8px;
    margin-bottom: 14px;
  }
  h2 { font-size: 24px; color: #1d4ed8; margin-bottom: 12px; }
  h3 { font-size: 20px; color: #334155; margin-bottom: 8px; }
  table { font-size: 14px; width: 100%; border-collapse: collapse; margin: 10px 0; }
  th { background-color: #f1f5f9; color: #1e293b; padding: 6px 10px; border: 1px solid #cbd5e1; font-weight: 600; }
  td { padding: 5px 8px; border: 1px solid #e2e8f0; }
  blockquote { font-size: 15px; background: #f8fafc; border-left: 5px solid #2563eb; padding: 10px 14px; margin: 12px 0; color: #334155; border-radius: 0 6px 6px 0; }
  .highlight { color: #2563eb; font-weight: 700; }
  .badge { background-color: #dbeafe; color: #1e40af; padding: 3px 10px; border-radius: 4px; font-size: 13px; font-weight: 600; }
  .card-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin-top: 10px; }
  .card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px; }
  img { display: block; margin: 10px auto; max-height: 390px; max-width: 95%; object-fit: contain; border-radius: 6px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08); }
  .split-layout {
    display: flex; gap: 22px; align-items: center; justify-content: space-between;
  }
  .split-left { flex: 1.05; min-width: 0; }
  .split-right { flex: 1.15; text-align: center; min-width: 0; }
  .split-right img {
    max-height: 420px; width: 100%; object-fit: contain; margin: 0 auto;
    border-radius: 6px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
  }
  .section-divider {
    display: flex; flex-direction: column; justify-content: center; height: 100%; text-align: left;
    padding: 30px 40px; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: #ffffff; border-radius: 12px;
  }
---
```

---

## 3. 슬라이드 레이아웃 유형별 템플릿

### 3.1 표지 슬라이드 (Title)
```markdown
<div style="display: flex; flex-direction: column; justify-content: center; height: 100%; text-align: center; padding-top: 40px;">

<span class="badge" style="align-self: center; font-size: 16px; padding: 6px 18px; margin-bottom: 20px;">
  보고서 분류명
</span>

<h1 style="font-size: 42px; line-height: 1.3; border-bottom: none; margin-bottom: 12px; color: #0f172a;">
  메인 타이틀<br><span style="color: #2563eb;">강조 서브 타이틀</span>
</h1>

<p style="font-size: 20px; color: #475569; margin-bottom: 35px;">
  핵심 가치 제안 및 분석 목표 한 줄 요약
</p>

<div style="font-size: 16px; color: #64748b; line-height: 1.8;">
  <strong>작성자</strong>: 수석 데이터 분석가 &nbsp;|&nbsp; 
  <strong>대상 데이터</strong>: <code>파일명.csv</code> (건수)<br>
  <strong>분석 환경</strong>: Python, Matplotlib, Scikit-learn
</div>

</div>

<!--
[발표자 노트 | 약 2분 분량]
(발표 오프닝, 분석 배경, 청중 환영 및 오늘 전달할 핵심 가치를 450~600자 구어체로 작성)
-->
```

### 3.2 섹션 간지 슬라이드 (Section Divider)
```markdown
<div class="section-divider">

<span class="badge" style="background-color: #3b82f6; color: #ffffff; align-self: flex-start; margin-bottom: 20px;">
  PART 1
</span>

<h1 style="font-size: 38px; color: #ffffff; border-bottom: 3px solid #3b82f6; padding-bottom: 12px; margin-bottom: 18px;">
  대주제 섹션 타이틀
</h1>

<p style="font-size: 20px; color: #cbd5e1; line-height: 1.6; margin: 0;">
  해당 파트에서 다룰 핵심 탐색 영역과 분석 관점에 대한 2줄 브리핑
</p>

</div>

<!--
[발표자 노트 | 약 2분 분량]
(이번 파트로 넘어가는 논리적 연결 고리, 다룰 핵심 질문 및 청중 안내 멘트)
-->
```

### 3.3 시각화 차트 슬라이드 (Visual Chart: 텍스트 왼쪽 + 그래프 오른쪽)
```markdown
# 순수 주제 타이틀 (번호 제외)

<div class="split-layout">
<div class="split-left">

### 핵심 관찰 지표 요약
| 지표명 | 표본수 | 평균 | 중앙값 | 비즈니스 평가 |
|:---|---:|---:|---:|:---|
| **측정변수** | 1,000 | 25,000원 | 24,000원 | 정상 수렴 |

- **주요 발견점**:
  - 핵심 관찰 포인트 1 (구간 밀집도 등)
  - 핵심 관찰 포인트 2 (이상치 및 경계선)

> **💡 분석가 해석**: 데이터 포인트가 던지는 핵심 시사점

</div>
<div class="split-right">

![대체텍스트](../images/01_distribution.png)

</div>
</div>

<!--
[발표자 노트 | 약 2분 분량]
(차트의 x축, y축, 주요 피크, 이상치, 하단 표의 수치적 특징을 상세히 구어체로 설명)
-->
```

### 3.4 2단 카드 그리드 슬라이드 (Card Grid)
```markdown
# 다차원 비교 분석

<div class="card-grid">

<div class="card">
  <h3 style="color: #2563eb; margin-bottom: 6px;">영역 A: 핵심 요인</h3>
  <ul style="font-size: 16px; margin: 0; padding-left: 20px;">
    <li>세부 관찰 포인트 1</li>
    <li>세부 관찰 포인트 2</li>
  </ul>
</div>

<div class="card">
  <h3 style="color: #2563eb; margin-bottom: 6px;">영역 B: 비즈니스 영향</h3>
  <ul style="font-size: 16px; margin: 0; padding-left: 20px;">
    <li>세부 관찰 포인트 1</li>
    <li>세부 관찰 포인트 2</li>
  </ul>
</div>

</div>

<!--
[발표자 노트 | 약 2분 분량]
(두 카드 간의 상호작용 및 비교 인사이트 설명)
-->
```

---

## 4. 발표자 노트(Presenter Notes) 작성 규칙

1. **포맷**: 반드시 `<!--`와 `-->` 블록 내부에 작성하며, 시작 줄에 `[발표자 노트 | 약 2분 분량]` 태그를 표기합니다.
2. **분량**: 슬라이드당 **최소 450자 ~ 최대 650자**를 준수합니다 (한국어 낭독 속도 기준 약 1분 50초 ~ 2분 10초).
3. **톤앤매너**: 격식 있고 신뢰감 있는 구어체("~를 살펴보겠습니다.", "~를 의미합니다.", "~가 강력히 권장됩니다.")를 사용합니다.
4. **내용 구조**:
   - `도입`: 이 슬라이드에서 청중이 주목해야 할 핵심 질문
   - `수치 설명`: 차트와 표에 드러난 주요 데이터 포인트 직접 언급
   - `인사이트/결론`: 이 데이터가 비즈니스나 의사결정에 던지는 구체적인 시사점

---

## 5. 30~32페이지 표준 슬라이드 덱 구조 권장안

- **01. 표지 (Title Slide)**
- **02. 전체 목차 (Agenda)**
- ──────── **[PART 1 간지] 분석 개요 및 데이터 무결성 검증**
- 04. 분석 배경 및 5대 핵심 목적
- 05. 데이터 수집 파이프라인 및 변수 스키마
- 06. 데이터 무결성 검증 (상위 vs 하위 샘플링)
- 07. 결측치 패턴 및 고유성 100% 검증
- 08. 수치형 변수 종합 기술통계
- 09. 범주형 변수 종합 기술통계
- ──────── **[PART 2 간지] 핵심 변수 일변량 심층 분석**
- 11. 판매가 분포 (차트 & 표)
- 12. 판매가 심층 분석 및 심리적 저항선
- 13. 평점 분포 (차트 & 표)
- 14. 평점 심층 분석 및 고득점 수렴 구조
- 15. 판매지수 Log10 분포 (차트 & 표)
- 16. 판매지수 멱법칙 및 파레토 법칙 해석
- 17. 출판연도별 점유 현황 (차트 & 표)
- 18. 신간 집중도와 스테디셀러의 생애주기
- ──────── **[PART 3 간지] 범주형 & 텍스트 마이닝 분석**
- 20. 상위 출판사별 배출 빈도 Top 30 (차트 & 표)
- 21. 출판사 과점 구조 및 브랜드 신뢰 효과
- 22. 주요 태그 빈도 분포 Top 30 (차트 & 표)
- 23. 구매 옵션 혜택과 기술 관심사의 결합
- 24. 도서명 TF-IDF 상위 30개 핵심 키워드 (차트 & 표)
- 25. 텍스트 마이닝 인사이트 (에이전틱 실무 전환)
- ──────── **[PART 4 간지] 다변량 관계 및 비즈니스 제언**
- 27. 출판사별 가격 vs 판매지수 매트릭스 (차트 & 표)
- 28. 가격대별 판매지수 상자그림 Boxplot (차트 & 표)
- 29. 평점 vs 리뷰수 산점도 및 수렴 분석 (차트 & 표)
- 30. 주요 변수 상관계수 행렬 히트맵 (차트 & 표)
- 31. 출판연도 × 가격대 피봇 히트맵 (차트 & 표)
- 32. 수석 분석가의 3대 핵심 비즈니스 제언
- 33. 엔지니어링 및 분석 품질 검증 통과 내역
- 34. 결언 및 질의응답 (Q&A)

---

## 6. 품질 검증 체크리스트

슬라이드 작성 완료 후 다음 7개 항목을 반드시 자체 검증합니다:

1. [ ] `header` 및 `footer` 전역 메타데이터가 완전히 배제되었는가?
2. [ ] `paginate: false`로 설정되어 페이지 번호가 노출되지 않는가?
3. [ ] 모든 슬라이드 제목과 표에서 `1.`, `Slide 1`, `[차트 01]` 등 일체의 번호가 제거되었는가?
4. [ ] 시각화 이미지가 표준 마크다운 문법(`![대체텍스트](../images/...)`)으로 선명하게 삽입되었는가?
5. [ ] 주요 파트마다 다크 테마 간지 슬라이드가 적재적소에 배치되었는가?
6. [ ] **모든 슬라이드에 450~650자(2분 분량)의 전문 발표자 노트가 누락 없이 수록되었는가?**
7. [ ] 모든 텍스트와 주석이 100% 한국어로 작성되었는가?
