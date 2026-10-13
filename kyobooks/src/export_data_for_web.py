"""교보문고 IT 베스트셀러 웹 대시보드용 데이터 추출 및 자바스크립트 번들링 스크립트.

이 스크립트는 최신 교보문고 IT 베스트셀러 CSV 데이터를 로드하여
웹 대시보드(Chart.js)에서 즉시 활용할 수 있도록 파생 변수(가격대, 순위 구간, 출간 연도 등)를
계산하고, TF-IDF 핵심 키워드 및 메타데이터를 포함한 자바스크립트 번들 파일(data.js)로 내보냅니다.
브라우저에서 별도의 웹서버 없이 로컬 파일로 열더라도 CORS 제약 없이 동작할 수 있도록 지원합니다.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# 프로젝트 상대경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent  # kyobooks 디렉터리
DATA_DIR = BASE_DIR / "data"
WEBAPP_DIR = BASE_DIR / "src" / "webapp"


def get_latest_data_path() -> Path:
    """kyobooks/data 디렉터리에서 가장 최근의 베스트셀러 CSV 파일을 찾습니다."""
    csv_files = sorted(DATA_DIR.glob("kyobo_it_bestsellers_*.csv"), reverse=True)
    if csv_files:
        return csv_files[0]
    return DATA_DIR / "kyobo_it_bestsellers_20261013.csv"


def extract_tfidf_keywords(df: pd.DataFrame, top_n: int = 30) -> list[dict[str, object]]:
    """도서 소개 텍스트에서 TF-IDF 상위 N개 키워드를 추출합니다."""
    texts = df["inbukCntt"].dropna().astype(str).tolist()
    if not texts:
        return []

    korean_stopwords = {
        "수", "등", "및", "이", "그", "저", "위해", "통해", "대한", "관한",
        "제공", "수록", "구성", "활용", "책은", "있는", "하는", "따라", "함께",
        "가장", "완벽", "핵심", "기초", "실습", "다양한", "필요한", "도서", "독자",
        "출간", "개정판", "안내", "자세한", "설명", "내용", "과정", "이해",
    }

    tfidf = TfidfVectorizer(
        max_features=100,
        token_pattern=r"(?u)\b[가-힣a-zA-Z]{2,}\b",
        stop_words=list(korean_stopwords),
    )
    tfidf_mat = tfidf.fit_transform(texts)
    words = tfidf.get_feature_names_out()
    scores = tfidf_mat.sum(axis=0).A1

    tfidf_df = pd.DataFrame({"keyword": words, "score": np.round(scores, 2)})
    top_keywords = tfidf_df.sort_values("score", ascending=False).head(top_n)
    return top_keywords.to_dict(orient="records")


def export_data() -> None:
    """최신 CSV 데이터를 정제하여 webapp/data.js로 내보냅니다."""
    csv_path = get_latest_data_path()
    print(f"[정보] 데이터 로드 시작: {csv_path}")

    if not csv_path.exists():
        print(f"[오류] 데이터 파일이 존재하지 않습니다: {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    total_count = len(df)
    print(f"[정보] 원본 데이터 로드 완료: 총 {total_count:,}건")

    # 1. 결측치 및 타입 정제
    df["inbukCntt"] = df["inbukCntt"].fillna("")
    df["rating"] = df["rating"].fillna(0.0).round(2)
    df["review_count"] = df["review_count"].fillna(0).astype(int)
    df["original_price"] = df["original_price"].fillna(0).astype(int)
    df["sale_price"] = df["sale_price"].fillna(0).astype(int)
    df["discount_rate"] = df["discount_rate"].fillna(0).astype(int)

    # 2. 파생 변수 생성
    # 출간 연도
    df["pub_date_clean"] = pd.to_datetime(df["pub_date"], errors="coerce")
    df["pub_year"] = df["pub_date_clean"].dt.year.fillna(0).astype(int)

    # 가격대 구간
    bins_price = [0, 20000, 30000, 40000, float("inf")]
    labels_price = ["2만원 이하", "2만~3만원", "3만~4만원", "4만원 초과"]
    df["price_tier"] = pd.cut(df["sale_price"], bins=bins_price, labels=labels_price).astype(str)

    # 순위 구간 (Tier)
    max_rank = max(500, int(df["rank"].max()))
    bins_rank = [0, 50, 100, 200, max_rank]
    labels_rank = ["1~50위 (최상위)", "51~100위 (상위)", "101~200위 (중위)", "201위 이상 (하위)"]
    df["rank_tier"] = pd.cut(df["rank"], bins=bins_rank, labels=labels_rank).astype(str)

    # 3. TF-IDF 키워드 산출
    tfidf_keywords = extract_tfidf_keywords(df, 30)

    # 4. 상위 출판사 목록
    top_publishers = df["publisher"].value_counts().head(20).to_dict()

    # 5. 레코드 변환
    records = []
    for _, row in df.iterrows():
        records.append({
            "rank": int(row["rank"]),
            "title": str(row["title"]),
            "author": str(row["author"]),
            "publisher": str(row["publisher"]),
            "pub_date": str(row["pub_date"]),
            "pub_year": int(row["pub_year"]),
            "original_price": int(row["original_price"]),
            "sale_price": int(row["sale_price"]),
            "discount_rate": int(row["discount_rate"]),
            "rating": float(row["rating"]),
            "review_count": int(row["review_count"]),
            "isbn": str(row["isbn"]),
            "link": str(row["link"]),
            "price_tier": str(row["price_tier"]),
            "rank_tier": str(row["rank_tier"]),
        })

    # 6. 메타데이터 생성
    valid_ratings = df[df["rating"] > 0]["rating"]
    meta = {
        "generated_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_file": csv_path.name,
        "total_books": total_count,
        "avg_price": int(np.round(df["sale_price"].mean())),
        "median_price": int(df["sale_price"].median()),
        "avg_rating": round(float(valid_ratings.mean()), 2) if not valid_ratings.empty else 0.0,
        "avg_reviews": round(float(df["review_count"].mean()), 1),
        "total_reviews": int(df["review_count"].sum()),
        "books_2026": int((df["pub_year"] == 2026).sum()),
        "books_2026_pct": round(float((df["pub_year"] == 2026).sum() / total_count * 100), 1),
        "top_publishers": top_publishers,
        "tfidf_keywords": tfidf_keywords,
    }

    # 7. data.js 생성
    WEBAPP_DIR.mkdir(parents=True, exist_ok=True)
    out_js = WEBAPP_DIR / "data.js"

    bundle_obj = {
        "metadata": meta,
        "books": records,
    }

    js_content = (
        "// 교보문고 IT 베스트셀러 자동 생성 데이터 번들\n"
        f"// 기준 파일: {csv_path.name} (총 {total_count}건)\n"
        "window.KYOBO_DATA = "
        + json.dumps(bundle_obj, ensure_ascii=False, indent=2)
        + ";\n"
    )

    out_js.write_text(js_content, encoding="utf-8")
    print(f"[완료] 데이터 번들 생성 완료: {out_js} (크기: {out_js.stat().st_size:,} bytes)")


if __name__ == "__main__":
    export_data()
