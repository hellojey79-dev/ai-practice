"""교보문고 IT/컴퓨터 베스트셀러 데이터 탐색적 데이터 분석(EDA) 및 시각화 스크립트.

이 스크립트는 20년차 시니어 데이터 분석가의 방법론에 따라 교보문고 IT/컴퓨터 베스트셀러
데이터셋의 5단계 기본 탐색, 범주형/텍스트(TF-IDF) 특화 분석, 12종의 일변량/이변량/다변량
시각화 차트 생성 및 통계표 산출을 자동으로 수행합니다.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

# Windows 콘솔 인코딩 대응
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import koreanize_matplotlib  # 한글 폰트 설정 필수
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# 프로젝트 상대경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent  # kyobooks 디렉터리
IMAGES_DIR = BASE_DIR / "images"


def get_latest_data_path() -> Path:
    """kyobooks/data 디렉터리에서 가장 최근의 베스트셀러 CSV 파일을 찾습니다."""
    data_dir = BASE_DIR / "data"
    csv_files = sorted(data_dir.glob("kyobo_it_bestsellers_*.csv"), reverse=True)
    if csv_files:
        return csv_files[0]
    return data_dir / "kyobo_it_bestsellers_20261012.csv"


DATA_PATH = get_latest_data_path()


def run_basic_exploration(df: pd.DataFrame) -> dict[str, str]:
    """데이터 기본 탐색 5단계 프로세스를 실행하고 결과를 출력 및 반환합니다."""
    results: dict[str, str] = {}

    print("=" * 60)
    print("1. 상위 5개 행 & 하위 5개 행")
    print("=" * 60)
    print("=== 상위 5개 행 ===")
    print(df.head())
    print("\n=== 하위 5개 행 ===")
    print(df.tail())

    print("\n" + "=" * 60)
    print("2. 데이터 기본 정보 (info)")
    print("=" * 60)
    df.info()

    print("\n" + "=" * 60)
    print("3. 전체 행과 열의 수 (shape)")
    print("=" * 60)
    shape_msg = f"전체 데이터 규모: {df.shape[0]:,}개 행, {df.shape[1]:,}개 열"
    print(shape_msg)
    results["shape"] = shape_msg

    print("\n" + "=" * 60)
    print("4. 중복 데이터 확인")
    print("=" * 60)
    dup_cnt = int(df.duplicated().sum())
    dup_msg = f"중복 데이터 수: {dup_cnt:,}개"
    print(dup_msg)
    results["duplicated"] = dup_msg

    print("\n" + "=" * 60)
    print("5. 수치형 및 범주형 기술통계 산출")
    print("=" * 60)
    print("=== 수치형 변수 기술통계 ===")
    desc_num = df.describe()
    print(desc_num)

    print("\n=== 범주형 변수 기술통계 ===")
    desc_cat = df.select_dtypes(include=["object", "string", "category"]).describe()
    print(desc_cat)

    return results


def extract_tfidf_keywords(
    df: pd.DataFrame, text_col: str = "inbukCntt", top_n: int = 30
) -> pd.DataFrame:
    """텍스트 데이터에서 TF-IDF를 이용해 상위 N개 키워드를 추출합니다."""
    # 텍스트 결측치 처리 및 전처리
    texts = df[text_col].dropna().astype(str).tolist()

    # 한국어 불용어 및 단순 숫자/단문자 제외용 정규표현식 토큰 패턴
    # 2글자 이상의 한글, 영문 단어 추출
    token_pattern = r"(?u)\b[가-힣a-zA-Z]{2,}\b"

    # 추가 불용어 리스트 정의
    korean_stopwords = {
        "수", "등", "및", "이", "그", "저", "위해", "통해", "대한", "관한",
        "제공", "수록", "구성", "활용", "책은", "있는", "하는", "따라", "함께",
        "가장", "완벽", "핵심", "기초", "실습", "다양한", "필요한", "도서", "독자",
        "출간", "개정판", "안내", "자세한", "설명", "내용", "과정", "이해",
    }

    tfidf = TfidfVectorizer(
        max_features=100,
        token_pattern=token_pattern,
        stop_words=list(korean_stopwords),
    )
    tfidf_mat = tfidf.fit_transform(texts)
    words = tfidf.get_feature_names_out()
    scores = tfidf_mat.sum(axis=0).A1

    tfidf_df = pd.DataFrame({"키워드": words, "TF-IDF 점수": scores})
    tfidf_df = tfidf_df.sort_values("TF-IDF 점수", ascending=False).head(top_n).reset_index(drop=True)
    return tfidf_df


def generate_visualizations(df: pd.DataFrame) -> None:
    """12종의 일변량/이변량/다변량 차트를 생성하여 images/ 디렉토리에 저장합니다."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------
    # 차트 1: [일변량] 도서 정가 및 판매가 분포 (히스토그램 & 밀도)
    # -------------------------------------------------------------
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.hist(df["original_price"] / 1000, bins=25, color="#3498db", edgecolor="black", alpha=0.7)
    plt.title("정가(천원 단위) 분포", fontsize=13, fontweight="bold")
    plt.xlabel("정가 (천원)")
    plt.ylabel("도서 수 (권)")
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    plt.subplot(1, 2, 2)
    plt.hist(df["sale_price"] / 1000, bins=25, color="#2ecc71", edgecolor="black", alpha=0.7)
    plt.title("판매가(천원 단위) 분포", fontsize=13, fontweight="bold")
    plt.xlabel("판매가 (천원)")
    plt.ylabel("도서 수 (권)")
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "01_price_distribution.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 차트 2: [일변량] 할인율(discount_rate) 분포 (박스플롯 및 빈도)
    # -------------------------------------------------------------
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.boxplot(df["discount_rate"], patch_artist=True,
                boxprops=dict(facecolor="#e74c3c", color="black"),
                medianprops=dict(color="yellow", linewidth=2))
    plt.title("할인율 박스플롯", fontsize=13, fontweight="bold")
    plt.ylabel("할인율 (%)")
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    plt.subplot(1, 2, 2)
    disc_counts = df["discount_rate"].value_counts().sort_index()
    plt.bar(disc_counts.index.astype(str), disc_counts.values, color="#e67e22", edgecolor="black")
    plt.title("할인율 구간별 빈도", fontsize=13, fontweight="bold")
    plt.xlabel("할인율 (%)")
    plt.ylabel("도서 수 (권)")
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "02_discount_rate_distribution.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 차트 3: [일변량] 독자 평점(rating) 분포
    # -------------------------------------------------------------
    valid_ratings = df[df["rating"] > 0]["rating"]
    plt.figure(figsize=(10, 5))
    plt.hist(valid_ratings, bins=20, color="#9b59b6", edgecolor="black", alpha=0.8)
    plt.axvline(valid_ratings.median(), color="red", linestyle="dashed", linewidth=2, label=f"중앙값: {valid_ratings.median():.2f}")
    plt.axvline(valid_ratings.mean(), color="blue", linestyle="dotted", linewidth=2, label=f"평균값: {valid_ratings.mean():.2f}")
    plt.title("IT/컴퓨터 베스트셀러 독자 평점 분포 (0점 제외)", fontsize=13, fontweight="bold")
    plt.xlabel("평점 (10점 만점)")
    plt.ylabel("도서 수 (권)")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "03_rating_distribution.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 차트 4: [일변량] 리뷰 수(review_count) 로그 분포
    # -------------------------------------------------------------
    plt.figure(figsize=(10, 5))
    valid_reviews = df[df["review_count"] > 0]["review_count"]
    log_reviews = np.log1p(valid_reviews)
    plt.hist(log_reviews, bins=25, color="#1abc9c", edgecolor="black", alpha=0.8)
    plt.title("독자 리뷰 수 로그 변환 분포 [log(1 + review_count)]", fontsize=13, fontweight="bold")
    plt.xlabel("로그 리뷰 수")
    plt.ylabel("도서 수 (권)")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "04_review_count_log_distribution.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 차트 5: [범주형/특화] 베스트셀러 최다 배출 상위 20대 출판사 빈도
    # -------------------------------------------------------------
    top20_pub = df["publisher"].value_counts().head(20)
    plt.figure(figsize=(12, 7))
    y_pos = np.arange(len(top20_pub))
    plt.barh(y_pos, top20_pub.values, color="#34495e", edgecolor="black")
    plt.yticks(y_pos, top20_pub.index, fontsize=10)
    plt.gca().invert_yaxis()
    plt.title("IT/컴퓨터 베스트셀러 최다 배출 상위 20대 출판사", fontsize=14, fontweight="bold")
    plt.xlabel("진입 도서 수 (권)")
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    for i, v in enumerate(top20_pub.values):
        plt.text(v + 0.3, i, f"{v}권", va="center", fontsize=9, fontweight="bold")
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "05_top_publishers.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 차트 6: [범주형/특화] 최다 저작 등록 상위 20대 저자/역자 빈도
    # -------------------------------------------------------------
    top20_auth = df["author"].value_counts().head(20)
    plt.figure(figsize=(12, 7))
    y_pos = np.arange(len(top20_auth))
    plt.barh(y_pos, top20_auth.index, color="#16a085", edgecolor="black")
    plt.yticks(y_pos, top20_auth.index, fontsize=10)
    plt.gca().invert_yaxis()
    plt.title("IT/컴퓨터 베스트셀러 최다 등록 상위 20대 저자/역자", fontsize=14, fontweight="bold")
    plt.xlabel("등록 도서 수 (권)")
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    for i, v in enumerate(top20_auth.values):
        plt.text(v + 0.1, i, f"{v}권", va="center", fontsize=9, fontweight="bold")
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "06_top_authors.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 차트 7: [텍스트/특화] 책 소개(inbukCntt) TF-IDF 상위 30대 키워드 가중치
    # -------------------------------------------------------------
    tfidf_df = extract_tfidf_keywords(df, "inbukCntt", 30)
    plt.figure(figsize=(12, 8))
    y_pos = np.arange(len(tfidf_df))
    plt.barh(y_pos, tfidf_df["TF-IDF 점수"], color="#2980b9", edgecolor="black")
    plt.yticks(y_pos, tfidf_df["키워드"], fontsize=10)
    plt.gca().invert_yaxis()
    plt.title("책 소개(inbukCntt) 기반 TF-IDF 상위 30대 핵심 키워드", fontsize=14, fontweight="bold")
    plt.xlabel("TF-IDF 가중치 합계")
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "07_tfidf_keywords_top30.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 차트 8: [이변량] 출판사별 평균 판매가 및 평균 평점 (상위 15대 출판사)
    # -------------------------------------------------------------
    top15_pubs = df["publisher"].value_counts().head(15).index
    pub_stats = df[df["publisher"].isin(top15_pubs)].groupby("publisher").agg({
        "sale_price": "mean",
        "rating": lambda x: x[x > 0].mean() if len(x[x > 0]) > 0 else 0,
        "title": "count"
    }).reindex(top15_pubs)

    fig, ax1 = plt.subplots(figsize=(14, 6))
    x = np.arange(len(pub_stats))
    width = 0.4

    color1 = "#2c3e50"
    ax1.set_xlabel("출판사명", fontsize=11, fontweight="bold")
    ax1.set_ylabel("평균 판매가 (원)", color=color1, fontsize=11, fontweight="bold")
    bars1 = ax1.bar(x - width/2, pub_stats["sale_price"], width, label="평균 판매가", color="#3498db", edgecolor="black")
    ax1.tick_params(axis="y", labelcolor=color1)
    ax1.set_xticks(x)
    ax1.set_xticklabels(pub_stats.index, rotation=35, ha="right", fontsize=10)

    ax2 = ax1.twinx()
    color2 = "#c0392b"
    ax2.set_ylabel("평균 평점 (10점 만점)", color=color2, fontsize=11, fontweight="bold")
    bars2 = ax2.bar(x + width/2, pub_stats["rating"], width, label="평균 평점", color="#e74c3c", edgecolor="black")
    ax2.tick_params(axis="y", labelcolor=color2)
    ax2.set_ylim(8.0, 10.2)

    plt.title("상위 15대 출판사별 평균 판매가 및 독자 평점 비교", fontsize=14, fontweight="bold")
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "08_pub_price_vs_rating.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 차트 9: [이변량] 판매가 vs 독자 평점 산점도 및 추세선
    # -------------------------------------------------------------
    rated_df = df[df["rating"] > 0]
    plt.figure(figsize=(10, 6))
    plt.scatter(rated_df["sale_price"] / 1000, rated_df["rating"],
                alpha=0.6, color="#8e44ad", edgecolors="black", s=rated_df["review_count"].clip(10, 300))
    # 선형 추세선
    m, b = np.polyfit(rated_df["sale_price"] / 1000, rated_df["rating"], 1)
    x_line = np.linspace(rated_df["sale_price"].min() / 1000, rated_df["sale_price"].max() / 1000, 100)
    plt.plot(x_line, m * x_line + b, color="red", linestyle="--", linewidth=2, label=f"추세선 (기울기: {m:.4f})")
    plt.title("도서 판매가 vs 독자 평점 상관관계 (원 크기: 리뷰 수)", fontsize=13, fontweight="bold")
    plt.xlabel("판매가 (천원)")
    plt.ylabel("평점 (10점 만점)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "09_scatter_price_vs_rating.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 차트 10: [이변량] 출간 연도별 베스트셀러 점유 추이 (시계열)
    # -------------------------------------------------------------
    df_date = df.copy()
    df_date["pub_year"] = pd.to_datetime(df_date["pub_date"], errors="coerce").dt.year
    year_counts = df_date["pub_year"].value_counts().sort_index()
    # 최근 6개년 중심 필터링
    recent_years = year_counts[year_counts.index >= 2020]
    plt.figure(figsize=(10, 5))
    plt.plot(recent_years.index.astype(int).astype(str), recent_years.values,
             marker="o", linewidth=2.5, markersize=8, color="#d35400")
    for x_val, y_val in zip(recent_years.index.astype(int).astype(str), recent_years.values):
        plt.text(x_val, y_val + 3, f"{y_val}권", ha="center", fontsize=10, fontweight="bold")
    plt.title("출간 연도별 베스트셀러 진입 도서 추이 (2020년 이후)", fontsize=13, fontweight="bold")
    plt.xlabel("출간 연도")
    plt.ylabel("진입 도서 수 (권)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "10_publication_year_trend.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 차트 11: [다변량] 수치형 변수 간 상관관계 히트맵
    # -------------------------------------------------------------
    corr_cols = ["rank", "original_price", "sale_price", "discount_rate", "rating", "review_count"]
    corr_labels = ["순위", "정가", "판매가", "할인율", "평점", "리뷰수"]
    corr_mat = df[corr_cols].corr()

    fig, ax = plt.subplots(figsize=(8, 7))
    cax = ax.matshow(corr_mat, cmap="coolwarm", vmin=-1, vmax=1)
    fig.colorbar(cax)
    ax.set_xticks(np.arange(len(corr_cols)))
    ax.set_yticks(np.arange(len(corr_cols)))
    ax.set_xticklabels(corr_labels, fontsize=11, fontweight="bold")
    ax.set_yticklabels(corr_labels, fontsize=11, fontweight="bold")

    for i in range(len(corr_cols)):
        for j in range(len(corr_cols)):
            val = corr_mat.iloc[i, j]
            color = "white" if abs(val) > 0.5 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, fontsize=11, fontweight="bold")

    plt.title("베스트셀러 주요 수치형 변수 간 피어슨 상관계수 행렬\n", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "11_correlation_heatmap.png", dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # 차트 12: [다변량] 순위 구간(Tier)별 가격 및 평점 특성 비교 (박스플롯)
    # -------------------------------------------------------------
    df_tier = df.copy()
    max_rank = max(500, int(df["rank"].max()))
    bins = [0, 50, 100, 200, max_rank]
    labels = ["1~50위 (최상위)", "51~100위 (상위)", "101~200위 (중위)", "201위 이상 (하위)"]
    df_tier["rank_tier"] = pd.cut(df_tier["rank"], bins=bins, labels=labels)

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    tier_groups_price = [group["sale_price"].values / 1000 for _, group in df_tier.groupby("rank_tier", observed=False)]
    plt.boxplot(tier_groups_price, tick_labels=labels, patch_artist=True,
                boxprops=dict(facecolor="#5dade2", color="black"),
                medianprops=dict(color="red", linewidth=2))
    plt.title("순위 구간별 판매가 분포 (천원)", fontsize=12, fontweight="bold")
    plt.ylabel("판매가 (천원)")
    plt.xticks(rotation=20, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    plt.subplot(1, 2, 2)
    tier_groups_rating = [group[group["rating"] > 0]["rating"].values for _, group in df_tier.groupby("rank_tier", observed=False)]
    plt.boxplot(tier_groups_rating, tick_labels=labels, patch_artist=True,
                boxprops=dict(facecolor="#f5b041", color="black"),
                medianprops=dict(color="red", linewidth=2))
    plt.title("순위 구간별 평점 분포 (0점 제외)", fontsize=12, fontweight="bold")
    plt.ylabel("평점 (10점 만점)")
    plt.xticks(rotation=20, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "12_rank_tier_comparison.png", dpi=300)
    plt.close()

    print("\n[완료] 총 12종의 시각화 차트가 images/ 폴더에 성공적으로 생성 및 저장되었습니다.")


def compute_all_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """리포트에 첨부할 모든 수치 통계표, 피봇테이블, 교차표를 산출합니다."""
    tables: dict[str, pd.DataFrame] = {}

    # 표 1: 가격 구간별 도서 수 및 통계
    df["price_bin"] = pd.cut(df["sale_price"], bins=[0, 20000, 30000, 40000, float("inf")],
                             labels=["2만원 이하", "2만~3만원", "3만~4만원", "4만원 초과"])
    tables["price_bin"] = df.groupby("price_bin", observed=False).agg(
        도서수=("rank", "count"),
        평균정가=("original_price", "mean"),
        평균판매가=("sale_price", "mean"),
        평균할인율=("discount_rate", "mean"),
        평균평점=("rating", lambda x: round(x[x > 0].mean(), 2)),
    ).reset_index()

    # 표 2: 할인율 빈도표
    tables["discount_counts"] = df["discount_rate"].value_counts().sort_index().reset_index()
    tables["discount_counts"].columns = ["할인율(%)", "도서수(권)"]

    # 표 3: 평점 구간별 통계
    df["rating_bin"] = pd.cut(df[df["rating"] > 0]["rating"], bins=[0, 8.5, 9.0, 9.5, 10.0],
                              labels=["8.5점 미만", "8.5~9.0점", "9.0~9.5점", "9.5~10.0점"])
    tables["rating_bin"] = df.groupby("rating_bin", observed=False).agg(
        도서수=("rank", "count"),
        평균리뷰수=("review_count", "mean"),
        평균판매가=("sale_price", "mean"),
    ).reset_index()

    # 표 4: 리뷰 수 구간별 통계
    df["review_bin"] = pd.cut(df["review_count"], bins=[-1, 0, 10, 50, 100, 10000],
                              labels=["리뷰 없음(0개)", "1~10개", "11~50개", "51~100개", "100개 초과"])
    tables["review_bin"] = df.groupby("review_bin", observed=False).agg(
        도서수=("rank", "count"),
        평균평점=("rating", lambda x: round(x[x > 0].mean(), 2)),
        평균순위=("rank", "mean"),
    ).reset_index()

    # 표 5: 상위 20대 출판사 집계
    tables["top_publishers"] = df["publisher"].value_counts().head(20).reset_index()
    tables["top_publishers"].columns = ["출판사", "도서수(권)"]

    # 표 6: 상위 20대 저자 집계
    tables["top_authors"] = df["author"].value_counts().head(20).reset_index()
    tables["top_authors"].columns = ["저자/역자", "도서수(권)"]

    # 표 7: TF-IDF 상위 30대 키워드
    tables["tfidf_keywords"] = extract_tfidf_keywords(df, "inbukCntt", 30)

    # 표 8: 상위 15대 출판사 상세 성과 비교 (피봇/교차 집계)
    top15 = df["publisher"].value_counts().head(15).index
    tables["pub_performance"] = df[df["publisher"].isin(top15)].groupby("publisher").agg(
        진입도서수=("rank", "count"),
        평균순위=("rank", "mean"),
        평균판매가=("sale_price", "mean"),
        평균평점=("rating", lambda x: round(x[x > 0].mean(), 2) if len(x[x > 0]) > 0 else 0),
        총리뷰수=("review_count", "sum"),
    ).loc[top15].reset_index()

    # 표 9: 상관관계 행렬
    corr_cols = ["rank", "original_price", "sale_price", "discount_rate", "rating", "review_count"]
    tables["correlation"] = df[corr_cols].corr().round(3).reset_index()

    # 표 10: 순위 구간(Tier)별 피봇테이블
    max_rank = max(500, int(df["rank"].max()))
    bins = [0, 50, 100, 200, max_rank]
    labels = ["1~50위", "51~100위", "101~200위", "201위 이상"]
    df["rank_tier"] = pd.cut(df["rank"], bins=bins, labels=labels)
    tables["tier_pivot"] = pd.pivot_table(
        df,
        index="rank_tier",
        observed=False,
        values=["sale_price", "discount_rate", "rating", "review_count"],
        aggfunc={
            "sale_price": ["mean", "median"],
            "discount_rate": "mean",
            "rating": lambda x: round(x[x > 0].mean(), 2),
            "review_count": ["mean", "sum"],
        }
    )

    return tables


def main() -> None:
    """EDA 스크립트 실행 메인 함수."""
    parser = argparse.ArgumentParser(description="교보문고 IT 베스트셀러 EDA 분석기")
    parser.add_argument(
        "--data-path",
        type=str,
        default=None,
        help="분석할 CSV 파일 경로 (미지정 시 data/ 디렉터리 내 최신 파일 자동 선택)",
    )
    args = parser.parse_args()

    target_data_path = Path(args.data_path) if args.data_path else get_latest_data_path()

    print("=" * 60)
    print("📊 20년차 시니어 데이터 분석가 EDA 파이프라인 가동")
    print(f"- 대상 데이터 파일: {target_data_path}")
    print("=" * 60)

    if not target_data_path.exists():
        print(f"[오류] 데이터 파일이 존재하지 않습니다: {target_data_path}")
        return

    df = pd.read_csv(target_data_path)
    print(f"[정보] 데이터 로드 완료: {target_data_path} (규모: {df.shape})")

    # 1. 5단계 기본 탐색 실행
    run_basic_exploration(df)

    # 2. 12종 시각화 생성 및 images/ 저장
    generate_visualizations(df)

    # 3. 통계표 산출
    tables = compute_all_tables(df)
    print(f"\n[완료] 총 {len(tables)}개 통계표 및 피봇 테이블 산출 완료")


if __name__ == "__main__":
    main()
