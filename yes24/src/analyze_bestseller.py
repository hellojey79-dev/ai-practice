"""YES24 베스트셀러 수집 데이터 탐색적 데이터 분석(EDA) 및 시각화 스크립트.

이 스크립트는 `yes24/data/yes24_bestseller.csv`에 저장된 베스트셀러 도서 목록 데이터를 불러와
결측치 정제 및 수치형 변환을 수행하고, 도서 시장의 가격, 출판사, 키워드, 판매지수 트렌드를
분석하여 6가지 고해상도 시각화 차트(`yes24/images/*.png`)를 생성합니다.

[주요 기능]
1. 데이터 로드 및 전처리 (`load_and_preprocess_data`):
   - 가격, 평점, 리뷰수, 판매지수, 할인율의 수치형 변환 및 결측치 보정
   - 출판일에서 출판연도 및 출판월 파생 변수 추출
2. 가격 및 할인율 분포 시각화 (`plot_price_distribution`):
   - 정가/판매가 히스토그램 및 박스플롯 생성
3. 최다 진입 출판사 TOP 10 분석 (`plot_top_publishers`):
   - 베스트셀러 목록 내 출판사별 점유 도서 수 가로 막대 차트
4. 판매지수 상위 도서 TOP 10 분석 (`plot_top_sales_index`):
   - 독자들의 실제 구매 반응을 나타내는 판매지수 최상위 도서 시각화
5. 평점 vs 리뷰 수 vs 판매지수 상관관계 (`plot_rating_review_scatter`):
   - 평점과 독자 참여도(리뷰 수)의 분포 및 관계 산점도
6. 인기 키워드 태그 빈도 분석 (`plot_tag_frequencies`):
   - 도서에 부여된 해시태그 중 최빈출 상위 15개 키워드 시각화
7. 출판 연도별 분포 분석 (`plot_publish_year_trend`):
   - 최근 신간과 과거 스테디셀러의 베스트셀러 진입 비중 분석

- 작성일: 2026-10-09
- 입력 경로: yes24/data/yes24_bestseller.csv
- 출력 경로: yes24/images/01~06_*.png
"""

import os
import re
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# 한글 폰트 설정 (koreanize-matplotlib 우선 적용 후 Windows 시스템 폰트 폴백)
try:
    import koreanize_matplotlib
except ImportError:
    plt.rcParams["font.family"] = "Malgun Gothic"

plt.rcParams["axes.unicode_minus"] = False

# 시각화 전역 스타일 설정
sns.set_theme(style="whitegrid", font="Malgun Gothic" if "Malgun Gothic" in plt.rcParams["font.family"] else None)
plt.rcParams["axes.unicode_minus"] = False

# 기본 상대 경로 설정
DEFAULT_CSV_PATHS = [
    os.path.join("yes24", "data", "yes24_bestseller.csv"),
    os.path.join("yes24", "data", "yes24_bestsellers.csv"),
]
OUTPUT_IMAGE_DIR = os.path.join("yes24", "images")


def resolve_csv_path() -> str:
    """존재하는 CSV 데이터 파일의 상대 경로를 반환합니다.

    Returns:
        str: 유효한 CSV 파일 경로.

    Raises:
        FileNotFoundError: 대상 CSV 파일이 존재하지 않는 경우 발생.
    """
    for path in DEFAULT_CSV_PATHS:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f"베스트셀러 CSV 파일을 찾을 수 없습니다: {DEFAULT_CSV_PATHS}")


def load_and_preprocess_data(csv_path: str) -> pd.DataFrame:
    """CSV 파일을 읽어 데이터 정제 및 수치형 타입 변환을 수행합니다.

    Args:
        csv_path (str): 입력 CSV 파일 경로.

    Returns:
        pd.DataFrame: 전처리가 완료된 도서 데이터프레임.
    """
    print(f"[데이터 로드] '{csv_path}' 파일을 로드합니다...")
    df = pd.read_csv(csv_path, encoding="utf-8-sig")

    print(f"[데이터 전처리] 총 {len(df)}건의 원본 데이터 정제를 시작합니다.")

    # 1. 순위 수치형 변환
    df["순위"] = pd.to_numeric(df["순위"], errors="coerce")

    # 2. 가격(판매가, 정가) 수치형 변환
    for col in ["판매가", "정가"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("원", "", regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 3. 할인율 수치형 변환 (% 기호 제거)
    if "할인율" in df.columns:
        df["할인율_수치"] = (
            df["할인율"]
            .astype(str)
            .str.replace("%", "", regex=False)
            .str.strip()
        )
        df["할인율_수치"] = pd.to_numeric(df["할인율_수치"], errors="coerce")

    # 4. 평점 수치형 변환
    if "평점" in df.columns:
        df["평점"] = pd.to_numeric(df["평점"], errors="coerce")

    # 5. 리뷰수 및 판매지수 수치형 변환
    for col in ["리뷰수", "판매지수"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # 6. 출판일에서 출판연도 및 월 추출 (예: '2026년 08월' -> 2026, 8)
    if "출판일" in df.columns:
        df["출판연도"] = df["출판일"].astype(str).str.extract(r"(\d{4})년")
        df["출판연도"] = pd.to_numeric(df["출판연도"], errors="coerce")
        df["출판월"] = df["출판일"].astype(str).str.extract(r"(\d{1,2})월")
        df["출판월"] = pd.to_numeric(df["출판월"], errors="coerce")

    # 7. 결측 텍스트 컬럼 기본값 처리
    text_cols = ["도서명", "부제목", "저자", "출판사", "태그"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)

    print("[데이터 전처리 완료] 정제 및 파생변수 생성이 완료되었습니다.")
    return df


def plot_price_distribution(df: pd.DataFrame, output_dir: str) -> str:
    """판매가 및 정가 분포와 할인율 분포를 시각화합니다.

    Args:
        df (pd.DataFrame): 전처리된 도서 데이터프레임.
        output_dir (str): 이미지 저장 대상 폴더 경로.

    Returns:
        str: 생성된 이미지 파일 경로.
    """
    output_path = os.path.join(output_dir, "01_price_distribution.png")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # 이상치 제외 (3만원 이하가 대다수이나 10만원 초과 서적 등 고려)
    price_data = df[df["판매가"] > 0]["판매가"].dropna()
    mean_val = price_data.mean()
    median_val = price_data.median()

    # 1. 판매가 분포 히스토그램 & KDE
    sns.histplot(price_data, bins=35, kde=True, color="#3498db", ax=axes[0])
    axes[0].axvline(mean_val, color="red", linestyle="--", linewidth=1.5, label=f"평균가: {mean_val:,.0f}원")
    axes[0].axvline(median_val, color="green", linestyle="-.", linewidth=1.5, label=f"중위수: {median_val:,.0f}원")
    axes[0].set_title("YES24 베스트셀러 도서 판매가 분포", fontsize=14, fontweight="bold", pad=12)
    axes[0].set_xlabel("판매가 (원)", fontsize=11)
    axes[0].set_ylabel("도서 수 (권)", fontsize=11)
    axes[0].set_xlim(0, 70000)
    axes[0].legend(fontsize=11)

    # 2. 할인율 분포
    discount_data = df[df["할인율_수치"].notna()]["할인율_수치"]
    sns.countplot(x=discount_data.astype(int), color="#2ecc71", ax=axes[1])
    axes[1].set_title("베스트셀러 도서 할인율 분포 (%)", fontsize=14, fontweight="bold", pad=12)
    axes[1].set_xlabel("할인율 (%)", fontsize=11)
    axes[1].set_ylabel("도서 수 (권)", fontsize=11)

    # 막대 위 수치 레이블 표기
    for p in axes[1].patches:
        h = p.get_height()
        if h > 0:
            axes[1].annotate(
                f"{int(h)}권",
                (p.get_x() + p.get_width() / 2.0, h),
                ha="center",
                va="bottom",
                fontsize=10,
                xytext=(0, 3),
                textcoords="offset points",
            )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[차트 저장] 1. 가격 분포 차트 생성 완료: {output_path}")
    return output_path


def plot_top_publishers(df: pd.DataFrame, output_dir: str) -> str:
    """베스트셀러 최다 진입 출판사 TOP 10을 시각화합니다.

    Args:
        df (pd.DataFrame): 전처리된 도서 데이터프레임.
        output_dir (str): 이미지 저장 대상 폴더 경로.

    Returns:
        str: 생성된 이미지 파일 경로.
    """
    output_path = os.path.join(output_dir, "02_top_publishers.png")
    top_pubs = (
        df[df["출판사"].str.strip() != ""]["출판사"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    top_pubs.columns = ["출판사", "도서수"]

    plt.figure(figsize=(12, 6.5))
    palette = sns.color_palette("Blues_r", n_colors=10)
    barplot = sns.barplot(
        data=top_pubs,
        y="출판사",
        x="도서수",
        hue="출판사",
        palette=palette,
        legend=False,
    )

    total_books = len(df)
    for p in barplot.patches:
        width = p.get_width()
        ratio = (width / total_books) * 100
        barplot.annotate(
            f" {int(width)}권 ({ratio:.1f}%)",
            (width, p.get_y() + p.get_height() / 2.0),
            ha="left",
            va="center",
            fontsize=10,
            fontweight="bold",
        )

    plt.title("YES24 베스트셀러 진입 도서 수 기준 상위 10개 출판사", fontsize=15, fontweight="bold", pad=15)
    plt.xlabel("베스트셀러 등록 도서 수 (권)", fontsize=11)
    plt.ylabel("출판사", fontsize=11)
    plt.xlim(0, top_pubs["도서수"].max() * 1.25)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[차트 저장] 2. 최다 진입 출판사 차트 생성 완료: {output_path}")
    return output_path


def plot_top_sales_index(df: pd.DataFrame, output_dir: str) -> str:
    """판매지수 기준 최상위 도서 TOP 10을 시각화합니다.

    Args:
        df (pd.DataFrame): 전처리된 도서 데이터프레임.
        output_dir (str): 이미지 저장 대상 폴더 경로.

    Returns:
        str: 생성된 이미지 파일 경로.
    """
    output_path = os.path.join(output_dir, "03_sales_index_top10.png")
    top_sales = df.sort_values(by="판매지수", ascending=False).head(10).copy()

    # 도서명이 너무 길 경우 앞 22자 추출
    top_sales["표시도서명"] = top_sales["도서명"].apply(
        lambda x: x[:22] + "..." if len(x) > 22 else x
    )

    plt.figure(figsize=(13, 7))
    palette = sns.color_palette("Oranges_r", n_colors=10)
    barplot = sns.barplot(
        data=top_sales,
        y="표시도서명",
        x="판매지수",
        hue="표시도서명",
        palette=palette,
        legend=False,
    )

    for p in barplot.patches:
        width = p.get_width()
        barplot.annotate(
            f" {int(width):,}점",
            (width, p.get_y() + p.get_height() / 2.0),
            ha="left",
            va="center",
            fontsize=10,
            fontweight="bold",
        )

    plt.title("YES24 베스트셀러 판매지수 TOP 10 도서", fontsize=15, fontweight="bold", pad=15)
    plt.xlabel("판매지수", fontsize=11)
    plt.ylabel("도서명", fontsize=11)
    plt.xlim(0, top_sales["판매지수"].max() * 1.22)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[차트 저장] 3. 판매지수 상위 도서 차트 생성 완료: {output_path}")
    return output_path


def plot_rating_review_scatter(df: pd.DataFrame, output_dir: str) -> str:
    """평점과 리뷰 수의 분포 및 판매지수와의 관계를 시각화합니다.

    Args:
        df (pd.DataFrame): 전처리된 도서 데이터프레임.
        output_dir (str): 이미지 저장 대상 폴더 경로.

    Returns:
        str: 생성된 이미지 파일 경로.
    """
    output_path = os.path.join(output_dir, "04_rating_review_scatter.png")
    valid_data = df[(df["평점"] > 0) & (df["리뷰수"] > 0)].copy()

    plt.figure(figsize=(11, 6.5))
    scatter = sns.scatterplot(
        data=valid_data,
        x="평점",
        y="리뷰수",
        size="판매지수",
        sizes=(40, 450),
        hue="판매지수",
        palette="viridis",
        alpha=0.75,
        edgecolor="black",
        linewidth=0.5,
    )

    plt.title("도서 평점 vs 리뷰 수 및 판매지수 분포", fontsize=15, fontweight="bold", pad=15)
    plt.xlabel("회원 평점 (10점 만점)", fontsize=11)
    plt.ylabel("리뷰 수 (건)", fontsize=11)
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", title="판매지수", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[차트 저장] 4. 평점 및 리뷰 산점도 생성 완료: {output_path}")
    return output_path


def plot_tag_frequencies(df: pd.DataFrame, output_dir: str) -> str:
    """베스트셀러 도서에 부여된 주요 키워드 태그의 빈도 상위 15개를 시각화합니다.

    Args:
        df (pd.DataFrame): 전처리된 도서 데이터프레임.
        output_dir (str): 이미지 저장 대상 폴더 경로.

    Returns:
        str: 생성된 이미지 파일 경로.
    """
    output_path = os.path.join(output_dir, "05_tag_frequency.png")
    all_tags: List[str] = []

    for tag_str in df["태그"].dropna():
        if not tag_str:
            continue
        # 태그 분리 ('#키워드' 또는 콤마 구분)
        tags = [t.strip().lstrip("#").strip() for t in tag_str.split(",") if t.strip()]
        all_tags.extend(tags)

    tag_series = pd.Series(all_tags)
    # 빈 값 또는 무의미한 특수문자 필터링
    tag_counts = tag_series[tag_series != ""].value_counts().head(15).reset_index()
    tag_counts.columns = ["태그", "빈도"]

    plt.figure(figsize=(12, 6.5))
    palette = sns.color_palette("mako", n_colors=15)
    barplot = sns.barplot(
        data=tag_counts,
        y="태그",
        x="빈도",
        hue="태그",
        palette=palette,
        legend=False,
    )

    for p in barplot.patches:
        width = p.get_width()
        barplot.annotate(
            f" {int(width)}회",
            (width, p.get_y() + p.get_height() / 2.0),
            ha="left",
            va="center",
            fontsize=10,
            fontweight="bold",
        )

    plt.title("YES24 베스트셀러 최빈출 키워드 태그 TOP 15", fontsize=15, fontweight="bold", pad=15)
    plt.xlabel("등장 빈도 (회)", fontsize=11)
    plt.ylabel("키워드 태그", fontsize=11)
    plt.xlim(0, tag_counts["빈도"].max() * 1.2)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[차트 저장] 5. 주요 태그 빈도 차트 생성 완료: {output_path}")
    return output_path


def plot_publish_year_trend(df: pd.DataFrame, output_dir: str) -> str:
    """출간 연도별 베스트셀러 분포(신간 vs 스테디셀러 비중)를 시각화합니다.

    Args:
        df (pd.DataFrame): 전처리된 도서 데이터프레임.
        output_dir (str): 이미지 저장 대상 폴더 경로.

    Returns:
        str: 생성된 이미지 파일 경로.
    """
    output_path = os.path.join(output_dir, "06_publish_year_distribution.png")
    year_df = df[df["출판연도"].notna()].copy()
    year_df["출판연도"] = year_df["출판연도"].astype(int)

    # 최근 10개년 중심 필터링 (2018년 이전은 '2018년 이전'으로 묶음)
    current_years = year_df["출판연도"].value_counts().sort_index()

    plt.figure(figsize=(12, 6))
    barplot = sns.barplot(
        x=current_years.index,
        y=current_years.values,
        color="#8e44ad",
    )

    for p in barplot.patches:
        h = p.get_height()
        if h > 0:
            barplot.annotate(
                f"{int(h)}권",
                (p.get_x() + p.get_width() / 2.0, h),
                ha="center",
                va="bottom",
                fontsize=10,
                xytext=(0, 3),
                textcoords="offset points",
            )

    plt.title("YES24 베스트셀러 진입 도서 출간 연도별 분포", fontsize=15, fontweight="bold", pad=15)
    plt.xlabel("출간 연도", fontsize=11)
    plt.ylabel("도서 수 (권)", fontsize=11)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[차트 저장] 6. 출간 연도별 분포 차트 생성 완료: {output_path}")
    return output_path


def print_summary_statistics(df: pd.DataFrame) -> Dict[str, any]:
    """분석 주요 핵심 지표를 요약하여 콘솔에 출력하고 딕셔너리로 반환합니다.

    Args:
        df (pd.DataFrame): 전처리된 도서 데이터프레임.

    Returns:
        Dict[str, any]: 주요 통계 요약 딕셔너리.
    """
    total_books = len(df)
    avg_sale_price = df["판매가"].mean()
    median_sale_price = df["판매가"].median()
    avg_discount = df["할인율_수치"].mean()
    avg_rating = df["평점"].dropna().mean()
    total_reviews = df["리뷰수"].sum()
    avg_reviews = df["리뷰수"].mean()

    top_publisher = df["출판사"].value_counts().index[0] if not df["출판사"].empty else "N/A"
    top_publisher_count = df["출판사"].value_counts().iloc[0] if not df["출판사"].empty else 0

    max_sales_book = df.loc[df["판매지수"].idxmax()] if not df.empty else None

    summary = {
        "총 도서 수": total_books,
        "평균 판매가": round(avg_sale_price, 1) if pd.notna(avg_sale_price) else 0,
        "중위수 판매가": round(median_sale_price, 1) if pd.notna(median_sale_price) else 0,
        "평균 할인율": f"{avg_discount:.1f}%" if pd.notna(avg_discount) else "N/A",
        "평균 평점": round(avg_rating, 2) if pd.notna(avg_rating) else 0,
        "총 리뷰 수": int(total_reviews),
        "도서당 평균 리뷰 수": round(avg_reviews, 1),
        "최다 진입 출판사": f"{top_publisher} ({top_publisher_count}권)",
        "최고 판매지수 도서": f"{max_sales_book['도서명']} ({max_sales_book['판매지수']:,}점)" if max_sales_book is not None else "N/A",
    }

    print("\n" + "=" * 60)
    print("           YES24 베스트셀러 데이터 분석 핵심 요약")
    print("=" * 60)
    for k, v in summary.items():
        print(f" - {k:<20}: {v}")
    print("=" * 60 + "\n")

    return summary


def main() -> None:
    """EDA 파이프라인 총괄 실행 함수."""
    # 1. 파일 경로 확인 및 이미지 폴더 생성
    csv_path = resolve_csv_path()
    os.makedirs(OUTPUT_IMAGE_DIR, exist_ok=True)

    # 2. 데이터 로드 및 전처리
    df = load_and_preprocess_data(csv_path)

    # 3. 주요 통계 콘솔 요약 출력
    print_summary_statistics(df)

    # 4. 시각화 차트 6종 생성 및 저장
    print("[시각화 진행] 6종의 고해상도 차트 생성을 시작합니다...")
    plot_price_distribution(df, OUTPUT_IMAGE_DIR)
    plot_top_publishers(df, OUTPUT_IMAGE_DIR)
    plot_top_sales_index(df, OUTPUT_IMAGE_DIR)
    plot_rating_review_scatter(df, OUTPUT_IMAGE_DIR)
    plot_tag_frequencies(df, OUTPUT_IMAGE_DIR)
    plot_publish_year_trend(df, OUTPUT_IMAGE_DIR)

    print("\n[EDA 완료] 모든 차트 생성이 성공적으로 완료되었습니다.")
    print(f"[저장 폴더] {OUTPUT_IMAGE_DIR}")


if __name__ == "__main__":
    main()
