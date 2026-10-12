# py-eda 핵심 코드 템플릿 및 구현 레퍼런스

20년차 데이터 분석가 스타일의 깔끔하고 견고한 EDA 코드 구현을 위한 참조 템플릿 모음입니다.

---

## 1. 초기 환경 설정 및 라이브러리 임포트

```python
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# 한글 폰트 설정 (koreanize-matplotlib 필수)
import koreanize_matplotlib

# seaborn은 데이터 시각화 보조용으로만 사용하며 스타일 함수는 호출하지 않음
import seaborn as sns

# 이미지 저장 폴더 준비 (상대경로)
IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)
```

---

## 2. 데이터 기본 무결성 검증 5단계

```python
def check_data_overview(df: pd.DataFrame):
    print("=" * 60)
    print("1. 상위 5개 행:")
    print(df.head(5))
    print("\n2. 하위 5개 행:")
    print(df.tail(5))
    
    print("\n3. 데이터 기본 정보 (info):")
    df.info()
    
    print(f"\n4. 데이터 크기: {df.shape[0]:,}개 행, {df.shape[1]:,}개 열")
    print(f"5. 중복 데이터 행 수: {df.duplicated().sum():,}개")
    
    print("\n6. 수치형 변수 기술통계:")
    print(df.describe())
    
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(cat_cols) > 0:
        print("\n7. 범주형 변수 기술통계:")
        print(df.describe(include=['O', 'category']))
    print("=" * 60)
```

---

## 3. 범주형 변수 빈도수 분석 (상위 30개 제한)

```python
def plot_categorical_frequency(df: pd.DataFrame, col: str, save_path: str):
    # 상위 30개 범주 추출
    top30 = df[col].value_counts().head(30)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    top30.plot(kind='bar', ax=ax, color='steelblue', edgecolor='black')
    ax.set_title(f"[{col}] 빈도수 상위 {len(top30)}개 분포", fontsize=14, pad=12)
    ax.set_xlabel(col, fontsize=12)
    ax.set_ylabel("빈도수", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    
    # 대응 통계표
    freq_df = top30.reset_index()
    freq_df.columns = [col, '빈도수']
    freq_df['비율(%)'] = (freq_df['빈도수'] / len(df) * 100).round(2)
    return freq_df
```

---

## 4. 텍스트 변수 TF-IDF 키워드 분석 (상위 30개)

```python
from sklearn.feature_extraction.text import TfidfVectorizer

def analyze_text_tfidf(df: pd.DataFrame, text_col: str, save_path: str):
    # 형태소 분석 없이 TfidfVectorizer로 신속하게 추출
    clean_series = df[text_col].dropna().astype(str)
    
    vectorizer = TfidfVectorizer(max_features=30)
    tfidf_matrix = vectorizer.fit_transform(clean_series)
    
    words = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.sum(axis=0).A1
    
    tfidf_df = pd.DataFrame({'키워드': words, 'TF-IDF 점수 합계': scores})
    tfidf_df = tfidf_df.sort_values(by='TF-IDF 점수 합계', ascending=False).reset_index(drop=True)
    
    # 시각화
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(tfidf_df['키워드'][::-1], tfidf_df['TF-IDF 점수 합계'][::-1], color='darkorange', edgecolor='black')
    ax.set_title(f"[{text_col}] TF-IDF 상위 30개 핵심 키워드", fontsize=14, pad=12)
    ax.set_xlabel("TF-IDF 점수 합계", fontsize=12)
    ax.set_ylabel("키워드", fontsize=12)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    
    return tfidf_df
```

---

## 5. 다차원 시각화 (일변량/이변량/다변량) 및 통계표 생성

### 일변량 (Univariate)
- 수치형 분포: 히스토그램 + 밀도곡선
- 동반 표: 왜도, 첨도, 분위수(25%, 50%, 75%), IQR, 결측률 기술통계표

### 이변량 (Bivariate)
- 수치형 vs 수치형: 산점도 (Scatter Plot) 및 추세선
- 범주형 vs 수치형: 그룹별 상자그림(Boxplot) 또는 그룹별 평균 막대그래프
- 범주형 vs 범주형: 교차표(`pd.crosstab(df[cat1], df[cat2], normalize='index') * 100`) 및 누적 막대그래프

### 다변량 (Multivariate)
- 상관관계 히트맵: `df.corr(numeric_only=True)`
- 범주형 세분화 이변량: `pd.pivot_table(df, values=num_col, index=cat1, columns=cat2, aggfunc=['mean', 'count'])`
- 3차원 버블차트 / Facet 분할 산점도

---

## 6. 시각화 해석 작성 가이드라인 (50자 이상 필수)

시각화 아래에는 반드시 다음과 같은 구조로 50자 이상의 전문적 해석을 포함합니다:

```markdown
> **[시각화 해석 및 통찰]**
> 해당 차트는 연령대별 구매 금액의 분포를 나타내며, 30대와 40대 집단에서 중앙값 150만 원 이상의 고액 결제 패턴이 집중되어 있음을 확인할 수 있습니다. 특히 40대 이상 집단에서는 상위 이상치(Outlier)가 다수 관측되므로, 프리미엄 멤버십 타겟 마케팅 전략 수립 시 핵심 타겟군으로 우선 고려해야 합니다. (총 154자)
```
