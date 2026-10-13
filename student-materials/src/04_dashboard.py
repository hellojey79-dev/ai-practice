"""교보문고 IT/컴퓨터 베스트셀러 인터랙티브 웹 대시보드 실습 스크립트.

이 스크립트는 Streamlit과 Plotly를 활용하여 교보문고 IT/컴퓨터 베스트셀러 데이터를
웹 브라우저 상에서 동적으로 탐색하고, 출판사별 시장 점유율, 가격-평점 상관관계,
TF-IDF 핵심 키워드 트렌드를 시각적으로 분석할 수 있는 실습용 대시보드 애플리케이션입니다.

주요 기능:
1. 실시간 도서 검색 및 다중 조건(가격대, 순위 구간, 출판사) 필터링
2. 핵심 성과 지표(총 도서 수, 평균 판매가, 평균 평점, 최고 할인율) 메트릭 카드 표시
3. 출판사별 평균 판매가 및 평점 비교 차트 (Plotly Bar)
4. 판매가 vs 독자 평점 버블 산점도 (Plotly Scatter)
5. 책 소개 기반 실시간 TF-IDF 상위 키워드 바 차트
6. 수집 원천 데이터셋 다운로드 및 표 뷰어

작성자: ai-practice 대시보드 튜터
생성일: 2026-10-14
"""

from __future__ import annotations

from pathlib import Path
import re

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.feature_extraction.text import TfidfVectorizer
import streamlit as st

# ==============================================================================
# 1. 페이지 레이아웃 및 스타일 설정
# ==============================================================================
st.set_page_config(
    page_title="교보문고 IT 베스트셀러 대시보드",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# student-materials 기준 상대경로
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def get_target_data_path() -> Path:
    """최신 CSV 또는 샘플 CSV 파일을 찾습니다."""
    csv_files = sorted(DATA_DIR.glob("kyobo_it_bestsellers_*.csv"), reverse=True)
    if csv_files:
        return csv_files[0]
    return DATA_DIR / "sample_kyobo_bestsellers.csv"


# 커스텀 CSS
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    .metric-label { font-size: 0.85rem; color: #64748B; font-weight: 600; }
    .metric-val { font-size: 1.6rem; color: #0F172A; font-weight: 800; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# 2. 데이터 로드 및 전처리 캐싱
# ==============================================================================
@st.cache_data
def load_and_preprocess_data() -> pd.DataFrame:
    """CSV 데이터를 로드하고 분석용 파생변수를 생성합니다."""
    path = get_target_data_path()
    if not path.exists():
        st.error(f"데이터 파일이 존재하지 않습니다: {path}")
        return pd.DataFrame()

    df = pd.read_csv(path)
    df["inbukCntt"] = df["inbukCntt"].fillna("")
    df["pub_date"] = pd.to_datetime(df["pub_date"], errors="coerce")
    df["pub_year"] = df["pub_date"].dt.year.fillna(0).astype(int)

    # 순위 구간
    max_rank = max(500, int(df["rank"].max())) if not df.empty else 500
    rank_bins = [0, 50, 100, 200, max_rank]
    rank_labels = ["1~50위", "51~100위", "101~200위", "201위 이상"]
    df["rank_tier"] = pd.cut(df["rank"], bins=rank_bins, labels=rank_labels)

    return df


df_raw = load_and_preprocess_data()

if df_raw.empty:
    st.warning("분석할 도서 데이터가 없습니다. 먼저 01_scraper.py를 실행하거나 샘플 데이터를 확인하세요.")
    st.stop()

# ==============================================================================
# 3. 사이드바 필터 컨트롤
# ==============================================================================
st.sidebar.header("🔍 도서 필터 옵션")

# 검색어 필터
search_query = st.sidebar.text_input("도서명 / 저자 / 출판사 검색", "")

# 순위 구간 필터
tiers = ["전체"] + list(df_raw["rank_tier"].dropna().unique())
selected_tier = st.sidebar.selectbox("순위 구간 (Tier)", tiers, index=0)

# 출판사 필터 (상위 20대 + 전체)
top_pubs = ["전체"] + list(df_raw["publisher"].value_counts().head(20).index)
selected_pub = st.sidebar.selectbox("주요 출판사 선택", top_pubs, index=0)

# 가격 슬라이더
min_p = int(df_raw["sale_price"].min())
max_p = int(df_raw["sale_price"].max())
price_range = st.sidebar.slider("판매가 범위 (원)", min_p, max_p, (min_p, max_p), step=1000)

# 필터 적용
filtered_df = df_raw.copy()
if search_query:
    q = search_query.strip().lower()
    filtered_df = filtered_df[
        filtered_df["title"].str.lower().str.contains(q, na=False)
        | filtered_df["author"].str.lower().str.contains(q, na=False)
        | filtered_df["publisher"].str.lower().str.contains(q, na=False)
    ]

if selected_tier != "전체":
    filtered_df = filtered_df[filtered_df["rank_tier"] == selected_tier]

if selected_pub != "전체":
    filtered_df = filtered_df[filtered_df["publisher"] == selected_pub]

filtered_df = filtered_df[
    (filtered_df["sale_price"] >= price_range[0])
    & (filtered_df["sale_price"] <= price_range[1])
]

# ==============================================================================
# 4. 메인 화면 구성
# ==============================================================================
st.markdown('<div class="main-title">📚 교보문고 IT/컴퓨터 베스트셀러 대시보드</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="sub-title">데이터 소스: {get_target_data_path().name} | 필터링 결과: <b>{len(filtered_df):,}권</b> (전체 {len(df_raw):,}권)</div>',
    unsafe_allow_html=True,
)

# 메트릭 카드 4종
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="metric-box"><div class="metric-label">선택 도서 수</div>'
                f'<div class="metric-val">{len(filtered_df):,}권</div></div>', unsafe_allow_html=True)
with c2:
    avg_price = filtered_df["sale_price"].mean() if not filtered_df.empty else 0
    st.markdown('<div class="metric-box"><div class="metric-label">평균 판매가</div>'
                f'<div class="metric-val">{avg_price:,.0f}원</div></div>', unsafe_allow_html=True)
with c3:
    valid_r = filtered_df[filtered_df["rating"] > 0]["rating"]
    avg_rating = valid_r.mean() if not valid_r.empty else 0
    st.markdown('<div class="metric-box"><div class="metric-label">평균 평점</div>'
                f'<div class="metric-val">{avg_rating:.2f}점</div></div>', unsafe_allow_html=True)
with c4:
    max_disc = filtered_df["discount_rate"].max() if not filtered_df.empty else 0
    st.markdown('<div class="metric-box"><div class="metric-label">최대 할인율</div>'
                f'<div class="metric-val">{max_disc}%</div></div>', unsafe_allow_html=True)

st.write("")

# 탭 구성
tab1, tab2, tab3, tab4 = st.tabs(["📊 차트 분석", "🏢 출판사 비교", "🧠 핵심 토픽(TF-IDF)", "📋 도서 목록"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("도서 판매가 vs 평점 상관관계")
        if not filtered_df.empty:
            scatter_df = filtered_df[filtered_df["rating"] > 0]
            fig_scatter = px.scatter(
                scatter_df,
                x="sale_price",
                y="rating",
                size="review_count",
                color="publisher",
                hover_name="title",
                labels={"sale_price": "판매가 (원)", "rating": "평점 (10점 만점)", "review_count": "리뷰 수"},
                title="판매가와 평점의 관계 (버블 크기: 리뷰 수)",
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("조건에 맞는 도서가 없습니다.")

    with col_b:
        st.subheader("판매가 분포 히스토그램")
        if not filtered_df.empty:
            fig_hist = px.histogram(
                filtered_df,
                x="sale_price",
                nbins=20,
                color_discrete_sequence=["#3498db"],
                labels={"sale_price": "판매가 (원)", "count": "도서 수"},
                title="판매가 구간별 도서 분포",
            )
            st.plotly_chart(fig_hist, use_container_width=True)

with tab2:
    st.subheader("상위 출판사별 도서 수 및 평균 판매가")
    if not filtered_df.empty:
        pub_summary = (
            filtered_df.groupby("publisher")
            .agg(도서수=("rank", "count"), 평균판매가=("sale_price", "mean"), 평균평점=("rating", "mean"))
            .reset_index()
            .sort_values("도서수", ascending=False)
            .head(15)
        )
        fig_pub = px.bar(
            pub_summary,
            x="publisher",
            y="도서수",
            color="평균판매가",
            color_continuous_scale="Viridis",
            labels={"publisher": "출판사", "도서수": "등록 도서 수 (권)"},
            title="상위 15대 출판사 진입 도서 수 (색상: 평균 판매가)",
        )
        st.plotly_chart(fig_pub, use_container_width=True)
        st.dataframe(pub_summary, use_container_width=True)

with tab3:
    st.subheader("책 소개(inbukCntt) 기반 실시간 TF-IDF 키워드")
    texts = filtered_df["inbukCntt"].dropna().astype(str).tolist()
    if texts:
        tfidf = TfidfVectorizer(
            max_features=20,
            token_pattern=r"(?u)\b[가-힣a-zA-Z]{2,}\b",
            stop_words=["수", "등", "및", "이", "그", "저", "위해", "통해", "대한", "제공", "수록", "책은", "있는", "하는"],
        )
        try:
            tfidf_mat = tfidf.fit_transform(texts)
            words = tfidf.get_feature_names_out()
            scores = tfidf_mat.sum(axis=0).A1
            kw_df = pd.DataFrame({"키워드": words, "점수": scores}).sort_values("점수", ascending=True)
            fig_kw = px.bar(kw_df, x="점수", y="키워드", orientation="h", title="상위 20대 핵심 키워드 가중치")
            st.plotly_chart(fig_kw, use_container_width=True)
        except Exception as e:
            st.info(f"키워드 추출 중: {e}")
    else:
        st.info("분석할 텍스트가 없습니다.")

with tab4:
    st.subheader("도서 상세 목록")
    cols_to_show = ["rank", "title", "author", "publisher", "sale_price", "rating", "review_count", "pub_date", "link"]
    st.dataframe(
        filtered_df[cols_to_show],
        column_config={"link": st.column_config.LinkColumn("상세 링크")},
        use_container_width=True,
    )
