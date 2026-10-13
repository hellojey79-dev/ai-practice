"""교보문고 IT/컴퓨터 베스트셀러 인터랙티브 웹 대시보드.

Streamlit과 Plotly를 활용하여 교보문고 IT/컴퓨터 베스트셀러 데이터를 다차원적으로
시각화하고 실시간 검색, 출판사 성과 분석, AI 토픽 탐색, 가격-평점 상관관계 분석을 제공합니다.
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
# 페이지 기본 설정
# ==============================================================================
st.set_page_config(
    page_title="교보문고 IT 베스트셀러 인사이트 대시보드",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 데이터 경로 (상대경로)
BASE_DIR = Path(__file__).resolve().parent.parent  # kyobooks 디렉터리


def get_latest_data_path() -> Path:
    """kyobooks/data 디렉터리에서 가장 최근의 베스트셀러 CSV 파일을 찾습니다."""
    data_dir = BASE_DIR / "data"
    csv_files = sorted(data_dir.glob("kyobo_it_bestsellers_*.csv"), reverse=True)
    if csv_files:
        return csv_files[0]
    return data_dir / "kyobo_it_bestsellers_20261012.csv"


DATA_PATH = get_latest_data_path()

# ==============================================================================
# 커스텀 CSS 스타일링
# ==============================================================================
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0F172A;
    }
    .book-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 10px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .rank-badge {
        display: inline-block;
        background: #3B82F6;
        color: white;
        font-weight: 700;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 0.8rem;
        margin-right: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# 데이터 로드 및 캐싱
# ==============================================================================
@st.cache_data
def load_data() -> pd.DataFrame:
    """교보문고 IT 베스트셀러 CSV 데이터를 로드하고 전처리합니다."""
    if not DATA_PATH.exists():
        st.error(f"데이터 파일을 찾을 수 없습니다: {DATA_PATH}")
        return pd.DataFrame()

    df = pd.read_csv(DATA_PATH)
    df["inbukCntt"] = df["inbukCntt"].fillna("")
    df["pub_date"] = pd.to_datetime(df["pub_date"], errors="coerce")
    df["pub_year"] = df["pub_date"].dt.year.fillna(0).astype(int)

    # 가격대 구간 생성
    bins = [0, 20000, 30000, 40000, float("inf")]
    labels = ["2만원 이하", "2만~3만원", "3만~4만원", "4만원 초과"]
    df["price_tier"] = pd.cut(df["sale_price"], bins=bins, labels=labels)

    # 순위 구간 생성
    max_rank = max(500, int(df["rank"].max())) if not df.empty else 500
    rank_bins = [0, 50, 100, 200, max_rank]
    rank_labels = ["1~50위 (최상위)", "51~100위 (상위)", "101~200위 (중위)", "201위 이상 (하위)"]
    df["rank_tier"] = pd.cut(df["rank"], bins=rank_bins, labels=rank_labels)

    return df


df_raw = load_data()

if df_raw.empty:
    st.stop()

# ==============================================================================
# 사이드바 (글로벌 필터)
# ==============================================================================
st.sidebar.header("🔍 도서 필터 옵션")

# 1. 검색어 필터
search_query = st.sidebar.text_input("도서명 / 저자 / 키워드 검색", placeholder="예: 클로드, ADsP, 파이썬...")

# 2. 순위 범위 슬라이더
min_rank, max_rank = int(df_raw["rank"].min()), int(df_raw["rank"].max())
selected_rank = st.sidebar.slider("순위 범위", min_rank, max_rank, (1, 100))

# 3. 판매가 범위 슬라이더
min_p, max_p = int(df_raw["sale_price"].min()), int(df_raw["sale_price"].max())
selected_price = st.sidebar.slider("판매가 범위 (원)", min_p, max_p, (min_p, max_p), step=1000)

# 4. 출판사 선택 필터
all_publishers = sorted(df_raw["publisher"].unique().tolist())
top_pubs_default = df_raw["publisher"].value_counts().head(5).index.tolist()
selected_publishers = st.sidebar.multiselect(
    "출판사 선택 (미선택 시 전체)",
    options=all_publishers,
    default=[],
)

# 5. 최소 평점 필터
min_rating = st.sidebar.slider("최소 평점 (0점 제외 도서)", 0.0, 10.0, 0.0, step=0.1)

# 데이터 필터링 적용
df_filtered = df_raw.copy()

# 순위 필터
df_filtered = df_filtered[
    (df_filtered["rank"] >= selected_rank[0]) & (df_filtered["rank"] <= selected_rank[1])
]

# 가격 필터
df_filtered = df_filtered[
    (df_filtered["sale_price"] >= selected_price[0])
    & (df_filtered["sale_price"] <= selected_price[1])
]

# 출판사 필터
if selected_publishers:
    df_filtered = df_filtered[df_filtered["publisher"].isin(selected_publishers)]

# 평점 필터
if min_rating > 0:
    df_filtered = df_filtered[df_filtered["rating"] >= min_rating]

# 검색어 필터
if search_query:
    q = search_query.strip().lower()
    df_filtered = df_filtered[
        df_filtered["title"].str.lower().str.contains(q, na=False)
        | df_filtered["author"].str.lower().str.contains(q, na=False)
        | df_filtered["publisher"].str.lower().str.contains(q, na=False)
        | df_filtered["inbukCntt"].str.lower().str.contains(q, na=False)
    ]

st.sidebar.markdown("---")
st.sidebar.info(f"📊 **필터 적용 결과**: **{len(df_filtered):,}권** / 전체 {len(df_raw):,}권")

# ==============================================================================
# 메인 헤더
# ==============================================================================
st.markdown('<div class="main-header">📚 교보문고 IT/컴퓨터 베스트셀러 대시보드</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">2026년 최신 IT 도서 트렌드, 출판사 점유율, 가격 정책 및 독자 반응 실시간 인터랙티브 분석</div>',
    unsafe_allow_html=True,
)

# ==============================================================================
# 메인 탭 네비게이션
# ==============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📊 핵심 KPI & 시장 요약",
        "🔍 인터랙티브 도서 탐색기",
        "🏢 출판사 & 저자 분석",
        "🤖 AI 키워드 & 토픽 분석",
        "📈 가격 vs 평점 상관관계",
    ]
)

# ------------------------------------------------------------------------------
# 탭 1: 핵심 KPI & 시장 요약
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("📌 IT/컴퓨터 도서 시장 핵심 지표 요약")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(
            f"""<div class="metric-card">
                <div class="metric-title">수집 도서 총수</div>
                <div class="metric-value">{len(df_filtered):,}권</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        avg_price = df_filtered["sale_price"].mean() if not df_filtered.empty else 0
        st.markdown(
            f"""<div class="metric-card">
                <div class="metric-title">평균 판매가</div>
                <div class="metric-value">{avg_price:,.0f}원</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        rated = df_filtered[df_filtered["rating"] > 0]
        avg_rating = rated["rating"].mean() if not rated.empty else 0
        st.markdown(
            f"""<div class="metric-card">
                <div class="metric-title">평균 평점 (유효)</div>
                <div class="metric-value">{avg_rating:.2f}점</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col4:
        max_rev = df_filtered["review_count"].max() if not df_filtered.empty else 0
        st.markdown(
            f"""<div class="metric-card">
                <div class="metric-title">최다 리뷰 수</div>
                <div class="metric-value">{max_rev:,}개</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col5:
        disc10_rate = (
            (df_filtered["discount_rate"] == 10).mean() * 100
            if not df_filtered.empty
            else 0
        )
        st.markdown(
            f"""<div class="metric-card">
                <div class="metric-title">10% 할인율 적용 비중</div>
                <div class="metric-value">{disc10_rate:.1f}%</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 차트 섹션 (가격대 비중 & 출간 연도 추이)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 💰 판매가 구간별 점유율")
        tier_counts = df_filtered["price_tier"].value_counts().reset_index()
        tier_counts.columns = ["가격구간", "도서수"]
        fig_pie = px.pie(
            tier_counts,
            values="도서수",
            names="가격구간",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320)
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.markdown("#### 📅 출간 연도별 도서 분포 (2020년 이후)")
        year_counts = (
            df_filtered[df_filtered["pub_year"] >= 2020]["pub_year"]
            .value_counts()
            .sort_index()
            .reset_index()
        )
        year_counts.columns = ["출간연도", "도서수"]
        fig_bar = px.bar(
            year_counts,
            x="출간연도",
            y="도서수",
            text="도서수",
            color="도서수",
            color_continuous_scale="Blues",
        )
        fig_bar.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320, coloraxis_showscale=False)
        fig_bar.update_xaxes(type="category")
        st.plotly_chart(fig_bar, use_container_width=True)

    # 최상위 5권 퀵 프리뷰
    st.markdown("#### 🏆 실시간 최상위 베스트셀러 Top 5")
    top5 = df_filtered.head(5)
    cols = st.columns(5)
    for idx, (_, row) in enumerate(top5.iterrows()):
        with cols[idx]:
            st.markdown(
                f"""
                <div style="background:#F1F5F9; border-radius:8px; padding:12px; height:100%;">
                    <span class="rank-badge">{row['rank']}위</span>
                    <strong style="font-size:0.95rem; color:#0F172A;">{row['title'][:22]}...</strong><br>
                    <small style="color:#475569;">저자: {row['author']}</small><br>
                    <small style="color:#64748B;">출판사: {row['publisher']}</small><br>
                    <div style="margin-top:8px;">
                        <span style="font-weight:700; color:#2563EB;">{row['sale_price']:,}원</span>
                        <span style="color:#EF4444; font-size:0.8rem;">({row['discount_rate']}%↓)</span>
                    </div>
                    <div style="font-size:0.8rem; color:#D97706; margin-top:4px;">★ {row['rating']} ({row['review_count']}리뷰)</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if row["link"]:
                st.link_button("교보문고 바로가기", row["link"], use_container_width=True)

# ------------------------------------------------------------------------------
# 탭 2: 인터랙티브 도서 탐색기
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("🔍 도서 실시간 검색 및 상세 탐색기")
    st.caption("사이드바의 필터 조건이 적용된 결과입니다. 도서를 선택하여 상세 책 소개를 확인하세요.")

    # 테이블 뷰
    display_cols = [
        "rank",
        "title",
        "author",
        "publisher",
        "pub_date",
        "sale_price",
        "discount_rate",
        "rating",
        "review_count",
    ]
    st.dataframe(
        df_filtered[display_cols].rename(
            columns={
                "rank": "순위",
                "title": "도서명",
                "author": "저자",
                "publisher": "출판사",
                "pub_date": "출간일",
                "sale_price": "판매가(원)",
                "discount_rate": "할인율(%)",
                "rating": "평점",
                "review_count": "리뷰수",
            }
        ),
        use_container_width=True,
        height=350,
    )

    st.markdown("---")
    st.subheader("📖 도서별 상세 카드 & 책 소개 보기")

    # 선택하여 상세보기
    book_titles = df_filtered["title"].tolist()
    if book_titles:
        selected_book_title = st.selectbox("상세 정보를 확인할 도서를 선택하세요:", book_titles)
        target_book = df_filtered[df_filtered["title"] == selected_book_title].iloc[0]

        b_col1, b_col2 = st.columns([1, 2])
        with b_col1:
            st.markdown(
                f"""
                ### {target_book['rank']}위. {target_book['title']}
                - **저자/역자**: `{target_book['author']}`
                - **출판사**: `{target_book['publisher']}`
                - **출간일**: `{str(target_book['pub_date'])[:10]}`
                - **ISBN**: `{target_book['isbn']}`
                - **정가 / 판매가**: {target_book['original_price']:,}원 ➔ **{target_book['sale_price']:,}원** ({target_book['discount_rate']}% 할인)
                - **평점 및 리뷰**: ⭐ **{target_book['rating']}점** (리뷰 {target_book['review_count']}개)
                """
            )
            if target_book["link"]:
                st.link_button("교보문고 공식 페이지 열기", target_book["link"], type="primary")

        with b_col2:
            st.markdown("#### 📝 책 상세 소개 (`inbukCntt`)")
            intro_text = target_book["inbukCntt"]
            if intro_text:
                st.text_area("도서 소개 전문", intro_text, height=260)
            else:
                st.info("등록된 책 소개가 없습니다.")
    else:
        st.warning("선택된 필터 조건에 부합하는 도서가 없습니다.")

# ------------------------------------------------------------------------------
# 탭 3: 출판사 & 저자 성과 분석
# ------------------------------------------------------------------------------
with tab3:
    st.subheader("🏢 주요 출판사 및 저자 성과 인터랙티브 분석")

    col_p1, col_p2 = st.columns([3, 2])
    with col_p1:
        st.markdown("#### 📊 최다 베스트셀러 배출 출판사 Top 15")
        top_pubs = df_filtered["publisher"].value_counts().head(15).reset_index()
        top_pubs.columns = ["출판사", "진입도서수"]
        fig_pubs = px.bar(
            top_pubs,
            x="진입도서수",
            y="출판사",
            orientation="h",
            text="진입도서수",
            color="진입도서수",
            color_continuous_scale="Teal",
        )
        fig_pubs.update_layout(yaxis=dict(autorange="reversed"), height=420, coloraxis_showscale=False)
        st.plotly_chart(fig_pubs, use_container_width=True)

    with col_p2:
        st.markdown("#### ✍️ 최다 등록 저자 / 연구진 Top 10")
        top_auth = df_filtered["author"].value_counts().head(10).reset_index()
        top_auth.columns = ["저자", "등록도서수"]
        fig_auth = px.bar(
            top_auth,
            x="등록도서수",
            y="저자",
            orientation="h",
            text="등록도서수",
            color="등록도서수",
            color_continuous_scale="Purples",
        )
        fig_auth.update_layout(yaxis=dict(autorange="reversed"), height=420, coloraxis_showscale=False)
        st.plotly_chart(fig_auth, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🎯 출판사 포지셔닝 맵 (평균 판매가 vs 평균 평점)")
    st.caption("버블 크기: 베스트셀러 진입 도서 권수 | 호버 시 상세 통계 확인 가능")

    # 상위 15대 출판사 집계
    major_pubs = df_raw["publisher"].value_counts().head(15).index
    pub_bubble = (
        df_raw[df_raw["publisher"].isin(major_pubs)]
        .groupby("publisher")
        .agg(
            진입권수=("rank", "count"),
            평균판매가=("sale_price", "mean"),
            평균평점=("rating", lambda x: x[x > 0].mean() if len(x[x > 0]) > 0 else 0),
            평균순위=("rank", "mean"),
        )
        .reset_index()
    )

    fig_bubble = px.scatter(
        pub_bubble,
        x="평균판매가",
        y="평균평점",
        size="진입권수",
        color="publisher",
        text="publisher",
        hover_data=["진입권수", "평균순위"],
        size_max=35,
    )
    fig_bubble.update_traces(textposition="top center")
    fig_bubble.update_layout(height=450, showlegend=False)
    st.plotly_chart(fig_bubble, use_container_width=True)

# ------------------------------------------------------------------------------
# 탭 4: AI 키워드 & 토픽 분석
# ------------------------------------------------------------------------------
with tab4:
    st.subheader("🤖 도서 소개 기반 TF-IDF 핵심 키워드 & AI 토픽 탐색")
    st.caption("생성형 AI, 바이브 코딩, 자격증 등 2026년 IT 도서 시장을 관통하는 핵심 키워드 분석")

    # TF-IDF 계산 (전체 데이터 기준)
    @st.cache_data
    def get_top_keywords() -> pd.DataFrame:
        texts = df_raw["inbukCntt"].dropna().astype(str).tolist()
        stopwords = {
            "수", "등", "및", "이", "그", "저", "위해", "통해", "대한", "관한",
            "제공", "수록", "구성", "활용", "책은", "있는", "하는", "따라", "함께",
            "가장", "완벽", "핵심", "기초", "실습", "다양한", "필요한", "도서", "독자",
            "출간", "개정판", "안내", "자세한", "설명", "내용", "과정", "이해",
        }
        tfidf = TfidfVectorizer(
            max_features=100,
            token_pattern=r"(?u)\b[가-힣a-zA-Z]{2,}\b",
            stop_words=list(stopwords),
        )
        mat = tfidf.fit_transform(texts)
        words = tfidf.get_feature_names_out()
        scores = mat.sum(axis=0).A1
        res = pd.DataFrame({"키워드": words, "가중치": scores})
        return res.sort_values("가중치", ascending=False).head(25)

    kw_df = get_top_keywords()

    k_col1, k_col2 = st.columns([3, 2])
    with k_col1:
        st.markdown("#### 🏷️ TF-IDF 상위 25대 핵심 키워드 가중치")
        fig_kw = px.bar(
            kw_df,
            x="가중치",
            y="키워드",
            orientation="h",
            color="가중치",
            color_continuous_scale="Viridis",
            text="가중치",
        )
        fig_kw.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_kw.update_layout(yaxis=dict(autorange="reversed"), height=480, coloraxis_showscale=False)
        st.plotly_chart(fig_kw, use_container_width=True)

    with k_col2:
        st.markdown("#### ⚡ 원클릭 토픽 필터링")
        st.caption("버튼을 클릭하면 해당 토픽을 다루는 베스트셀러를 즉시 확인합니다:")

        topic = st.radio(
            "인기 기술 토픽 선택:",
            ["전체", "인공지능 (AI)", "클로드 & 바이브 코딩", "데이터분석 & ADsP/SQLD", "자격증 수험서 (컴활/정처기)", "업무 자동화 & 엑셀"],
        )

        filter_kw = {
            "인공지능 (AI)": ["ai", "인공지능", "생성형", "chatgpt", "gpt"],
            "클로드 & 바이브 코딩": ["클로드", "claude", "바이브", "코워크", "스펙"],
            "데이터분석 & ADsP/SQLD": ["adsp", "sqld", "데이터 분석", "sql"],
            "자격증 수험서 (컴활/정처기)": ["컴활", "시나공", "이기적", "정보처리기사", "기출"],
            "업무 자동화 & 엑셀": ["엑셀", "업무", "자동화", "실무", "노션"],
        }

        if topic == "전체":
            sub_df = df_filtered
        else:
            patterns = "|".join(filter_kw[topic])
            sub_df = df_raw[
                df_raw["title"].str.contains(patterns, case=False, na=False)
                | df_raw["inbukCntt"].str.contains(patterns, case=False, na=False)
            ]

        st.success(f"**[{topic}]** 관련 도서: 총 **{len(sub_df)}권** 검색됨")
        for _, r in sub_df.head(6).iterrows():
            st.markdown(
                f"- **{r['rank']}위**: [{r['title']}]({r['link']}) ({r['publisher']} | {r['sale_price']:,}원)"
            )

# ------------------------------------------------------------------------------
# 탭 5: 가격 vs 평점 상관관계
# ------------------------------------------------------------------------------
with tab5:
    st.subheader("📈 도서 판매가와 독자 만족도(평점/리뷰) 상관관계 심층 분석")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("#### 🎯 판매가 vs 독자 평점 산점도")
        scatter_df = df_filtered[df_filtered["rating"] > 0]
        fig_scatter = px.scatter(
            scatter_df,
            x="sale_price",
            y="rating",
            size="review_count",
            color="discount_rate",
            hover_name="title",
            hover_data=["publisher", "rank", "sale_price", "review_count"],
            labels={"sale_price": "판매가 (원)", "rating": "평점 (10점 만점)", "discount_rate": "할인율(%)"},
            color_continuous_scale="Turbo",
            size_max=30,
        )
        fig_scatter.update_layout(height=380)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_s2:
        st.markdown("#### 📦 순위 티어(Tier)별 판매가 분포 (박스플롯)")
        fig_box = px.box(
            df_filtered,
            x="rank_tier",
            y="sale_price",
            color="rank_tier",
            labels={"rank_tier": "순위 구간", "sale_price": "판매가 (원)"},
        )
        fig_box.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🔢 주요 수치형 변수 간 피어슨 상관계수 매트릭스")
    corr_cols = ["rank", "original_price", "sale_price", "discount_rate", "rating", "review_count"]
    corr_labels = ["순위", "정가", "판매가", "할인율", "평점", "리뷰수"]
    corr_df = df_filtered[corr_cols].corr()
    corr_df.columns = corr_labels
    corr_df.index = corr_labels

    fig_heat = px.imshow(
        corr_df,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
    )
    fig_heat.update_layout(height=360)
    st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")
st.caption("데이터 수집 출처: 교보문고 공식 REST API | 분석 및 제작: 20년차 시니어 데이터 분석가 파이프라인")
