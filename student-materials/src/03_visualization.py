"""교보문고 IT 베스트셀러 12종 고해상도 시각화 차트 생성 실습 스크립트.

이 스크립트는 교보문고 IT/컴퓨터 베스트셀러 데이터셋을 바탕으로 일변량, 이변량, 다변량,
시계열 등 12가지 관점의 정밀 통계 차트를 자동 생성하여 images/ 디렉터리에 고해상도(DPI 300)
PNG 이미지로 저장하는 실습용 시각화 파이프라인입니다.

주요 기능:
1. koreanize-matplotlib 적용으로 한글 폰트 깨짐 원천 방지
2. Seaborn 전역 스타일 충돌을 배제한 순수 Matplotlib 정밀 스타일링
3. 12종 시각화: 가격 분포, 할인율, 평점, 출판사 순위, TF-IDF 키워드, 상관 히트맵 등
4. 상대경로 기준 student-materials/images/ 디렉터리 자동 생성 및 저장

작성자: ai-practice 시각화 튜터
생성일: 2026-10-14
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

# student-materials 기준 상대경로
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = BASE_DIR / "images"


def get_target_data_path(custom_path: str | None = None) -> Path:
    """분석 대상 CSV 경로를 찾습니다."""
    if custom_path:
        return Path(custom_path)
    csv_files = sorted(DATA_DIR.glob("kyobo_it_bestsellers_*.csv"), reverse=True)
    if csv_files:
        return csv_files[0]
    return DATA_DIR / "sample_kyobo_bestsellers.csv"


def extract_tfidf_keywords(df: pd.DataFrame, top_n: int = 30) -> pd.DataFrame:
    """책 소개(inbukCntt)에서 TF-IDF 상위 키워드를 추출합니다."""
    texts = df["inbukCntt"].dropna().astype(str).tolist()
    token_pattern = r"(?u)\b[가-힣a-zA-Z]{2,}\b"
    stopwords = {
        "수", "등", "및", "이", "그", "저", "위해", "통해", "대한", "관한",
        "제공", "수록", "구성", "활용", "책은", "있는", "하는", "따라", "함께",
        "가장", "완벽", "핵심", "기초", "실습", "다양한", "필요한", "도서", "독자",
        "출간", "개정판", "안내", "자세한", "설명", "내용", "과정", "이해",
    }
    tfidf = TfidfVectorizer(
        max_features=100,
        token_pattern=token_pattern,
        stop_words=list(stopwords),
    )
    tfidf_mat = tfidf.fit_transform(texts)
    words = tfidf.get_feature_names_out()
    scores = tfidf_mat.sum(axis=0).A1
    res_df = pd.DataFrame({"키워드": words, "TF-IDF점수": scores})
    return res_df.sort_values("TF-IDF점수", ascending=False).head(top_n).reset_index(drop=True)


def generate_all_visualizations(df: pd.DataFrame) -> None:
    """12종의 시각화 차트를 생성하여 images/ 디렉터리에 저장합니다."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[시작] 총 12종 시각화 차트 생성 진행 중 (저장 디렉터리: {IMAGES_DIR})...")

    # -------------------------------------------------------------
    # 차트 1: [일변량] 도서 정가 및 판매가 분포 (히스토그램)
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
    print("  - [1/12] 01_price_distribution.png 저장 완료")

    # -------------------------------------------------------------
    # 차트 2: [일변량] 할인율 분포 (박스플롯 & 빈도)
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
    print("  - [2/12] 02_discount_rate_distribution.png 저장 완료")

    # -------------------------------------------------------------
    # 차트 3: [일변량] 독자 평점 분포 (0점 제외)
    # -------------------------------------------------------------
    valid_ratings = df[df["rating"] > 0]["rating"]
    plt.figure(figsize=(10, 5))
    plt.hist(valid_ratings, bins=20, color="#9b59b6", edgecolor="black", alpha=0.8)
    if not valid_ratings.empty:
        plt.axvline(valid_ratings.median(), color="red", linestyle="dashed", linewidth=2, label=f"중앙값: {valid_ratings.median():.2f}")
        plt.axvline(valid_ratings.mean(), color="blue", linestyle="dotted", linewidth=2, label=f"평균값: {valid_ratings.mean():.2f}")
    plt.title("독자 평점 분포 (10점 만점)", fontsize=13, fontweight="bold")
    plt.xlabel("평점")
    plt.ylabel("도서 수 (권)")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "03_rating_distribution.png", dpi=300)
    plt.close()
    print("  - [3/12] 03_rating_distribution.png 저장 완료")

    # -------------------------------------------------------------
    # 차트 4: [일변량] 리뷰 수 로그 변환 분포
    # -------------------------------------------------------------
    valid_reviews = df[df["review_count"] > 0]["review_count"]
    log_reviews = np.log1p(valid_reviews) if not valid_reviews.empty else []
    plt.figure(figsize=(10, 5))
    plt.hist(log_reviews, bins=25, color="#1abc9c", edgecolor="black", alpha=0.8)
    plt.title("독자 리뷰 수 로그 변환 분포 [log(1 + review_count)]", fontsize=13, fontweight="bold")
    plt.xlabel("로그 리뷰 수")
    plt.ylabel("도서 수 (권)")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "04_review_count_log_distribution.png", dpi=300)
    plt.close()
    print("  - [4/12] 04_review_count_log_distribution.png 저장 완료")

    # -------------------------------------------------------------
    # 차트 5: [범주형] 최다 배출 상위 20대 출판사
    # -------------------------------------------------------------
    top20_pub = df["publisher"].value_counts().head(20)
    plt.figure(figsize=(12, 7))
    y_pos = np.arange(len(top20_pub))
    plt.barh(y_pos, top20_pub.values, color="#34495e", edgecolor="black")
    plt.yticks(y_pos, top20_pub.index, fontsize=10)
    plt.gca().invert_yaxis()
    plt.title("IT/컴퓨터 베스트셀러 최다 배출 상위 20대 출판사", fontsize=14, fontweight="bold")
    plt.xlabel("도서 수 (권)")
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    for i, v in enumerate(top20_pub.values):
        plt.text(v + 0.2, i, f"{v}권", va="center", fontsize=9, fontweight="bold")
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "05_top_publishers.png", dpi=300)
    plt.close()
    print("  - [5/12] 05_top_publishers.png 저장 완료")

    # -------------------------------------------------------------
    # 차트 6: [범주형] 최다 등록 상위 20대 저자/역자
    # -------------------------------------------------------------
    top20_auth = df["author"].value_counts().head(20)
    plt.figure(figsize=(12, 7))
    y_pos = np.arange(len(top20_auth))
    plt.barh(y_pos, top20_auth.index, color="#16a085", edgecolor="black")
    plt.yticks(y_pos, top20_auth.index, fontsize=10)
    plt.gca().invert_yaxis()
    plt.title("IT/컴퓨터 베스트셀러 최다 등록 상위 20대 저자/역자", fontsize=14, fontweight="bold")
    plt.xlabel("도서 수 (권)")
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    for i, v in enumerate(top20_auth.values):
        plt.text(v + 0.1, i, f"{v}권", va="center", fontsize=9, fontweight="bold")
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "06_top_authors.png", dpi=300)
    plt.close()
    print("  - [6/12] 06_top_authors.png 저장 완료")

    # -------------------------------------------------------------
    # 차트 7: [텍스트] 책 소개 TF-IDF 상위 30대 키워드
    # -------------------------------------------------------------
    tfidf_df = extract_tfidf_keywords(df, 30)
    plt.figure(figsize=(12, 8))
    y_pos = np.arange(len(tfidf_df))
    plt.barh(y_pos, tfidf_df["TF-IDF점수"], color="#2980b9", edgecolor="black")
    plt.yticks(y_pos, tfidf_df["키워드"], fontsize=10)
    plt.gca().invert_yaxis()
    plt.title("책 소개 기반 TF-IDF 상위 30대 핵심 기술 키워드", fontsize=14, fontweight="bold")
    plt.xlabel("TF-IDF 가중치 합계")
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "07_tfidf_keywords_top30.png", dpi=300)
    plt.close()
    print("  - [7/12] 07_tfidf_keywords_top30.png 저장 완료")

    # -------------------------------------------------------------
    # 차트 8: [이변량] 상위 15대 출판사별 평균 판매가 및 평점 이중 축 비교
    # -------------------------------------------------------------
    top15_pubs = df["publisher"].value_counts().head(15).index
    pub_stats = df[df["publisher"].isin(top15_pubs)].groupby("publisher").agg({
        "sale_price": "mean",
        "rating": lambda x: x[x > 0].mean() if len(x[x > 0]) > 0 else 0,
    }).reindex(top15_pubs)

    fig, ax1 = plt.subplots(figsize=(14, 6))
    x = np.arange(len(pub_stats))
    width = 0.4
    ax1.set_ylabel("평균 판매가 (원)", color="#2c3e50", fontsize=11, fontweight="bold")
    ax1.bar(x - width/2, pub_stats["sale_price"], width, label="평균 판매가", color="#3498db", edgecolor="black")
    ax1.set_xticks(x)
    ax1.set_xticklabels(pub_stats.index, rotation=35, ha="right", fontsize=10)

    ax2 = ax1.twinx()
    ax2.set_ylabel("평균 평점 (10점 만점)", color="#c0392b", fontsize=11, fontweight="bold")
    ax2.bar(x + width/2, pub_stats["rating"], width, label="평균 평점", color="#e74c3c", edgecolor="black")
    ax2.set_ylim(8.0, 10.2)

    plt.title("상위 15대 출판사별 평균 판매가 및 독자 평점 비교", fontsize=14, fontweight="bold")
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "08_pub_price_vs_rating.png", dpi=300)
    plt.close()
    print("  - [8/12] 08_pub_price_vs_rating.png 저장 완료")

    # -------------------------------------------------------------
    # 차트 9: [이변량] 판매가 vs 평점 상관 산점도 및 추세선
    # -------------------------------------------------------------
    rated_df = df[df["rating"] > 0]
    plt.figure(figsize=(10, 6))
    if len(rated_df) > 1:
        plt.scatter(rated_df["sale_price"] / 1000, rated_df["rating"],
                    alpha=0.6, color="#8e44ad", edgecolors="black", s=rated_df["review_count"].clip(10, 300))
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
    print("  - [9/12] 09_scatter_price_vs_rating.png 저장 완료")

    # -------------------------------------------------------------
    # 차트 10: [시계열] 출간 연도별 베스트셀러 점유 추이
    # -------------------------------------------------------------
    df_date = df.copy()
    df_date["pub_year"] = pd.to_datetime(df_date["pub_date"], errors="coerce").dt.year
    year_counts = df_date["pub_year"].value_counts().sort_index()
    recent_years = year_counts[year_counts.index >= 2020]
    plt.figure(figsize=(10, 5))
    if not recent_years.empty:
        plt.plot(recent_years.index.astype(int).astype(str), recent_years.values,
                 marker="o", linewidth=2.5, markersize=8, color="#d35400")
        for x_val, y_val in zip(recent_years.index.astype(int).astype(str), recent_years.values):
            plt.text(x_val, y_val + 1, f"{y_val}권", ha="center", fontsize=10, fontweight="bold")
    plt.title("출간 연도별 베스트셀러 진입 도서 추이 (2020년 이후)", fontsize=13, fontweight="bold")
    plt.xlabel("출간 연도")
    plt.ylabel("진입 도서 수 (권)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / "10_publication_year_trend.png", dpi=300)
    plt.close()
    print("  - [10/12] 10_publication_year_trend.png 저장 완료")

    # -------------------------------------------------------------
    # 차트 11: [다변량] 상관관계 히트맵
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
    print("  - [11/12] 11_correlation_heatmap.png 저장 완료")

    # -------------------------------------------------------------
    # 차트 12: [다변량] 순위 구간(Tier)별 판매가 및 평점 비교
    # -------------------------------------------------------------
    df_tier = df.copy()
    max_rank = max(500, int(df["rank"].max())) if not df.empty else 500
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
    print("  - [12/12] 12_rank_tier_comparison.png 저장 완료")

    print("\n[완료] 총 12종의 시각화 차트가 images/ 디렉터리에 성공적으로 저장되었습니다!")


def main() -> None:
    """메인 진입 함수."""
    parser = argparse.ArgumentParser(description="교보문고 IT 베스트셀러 12종 시각화 실습")
    parser.add_argument(
        "--data-path",
        type=str,
        default=None,
        help="시각화에 사용할 CSV 파일 경로 (미지정 시 최신 수집 데이터 자동 선택)",
    )
    args = parser.parse_args()

    target_path = get_target_data_path(args.data_path)
    print("=" * 60)
    print("🎨 [Step 3] 12종 고해상도 시각화 차트 생성 실습 시작")
    print(f"- 대상 데이터 파일: {target_path}")
    print("=" * 60)

    if not target_path.exists():
        print(f"[오류] 데이터 파일을 찾을 수 없습니다: {target_path}")
        return

    df = pd.read_csv(target_path)
    generate_all_visualizations(df)


if __name__ == "__main__":
    main()
