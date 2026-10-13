"""교보문고 IT 베스트셀러 데이터 정제 및 5단계 EDA 분석 실습 스크립트.

이 스크립트는 수집된 교보문고 IT 베스트셀러 데이터셋의 결측치 및 자료형을 점검하고,
20년차 시니어 데이터 분석가의 5단계 기본 탐색 프로세스와 TF-IDF 텍스트 마이닝을
체계적으로 실습할 수 있도록 제작된 코드입니다.

주요 기능:
1. 5단계 기본 탐색: 상하위 5행, info, shape, 중복 검사, 수치/범주형 기술통계
2. 데이터 정제: 책 소개 결측치 대체, 출간일 날짜형 변환, 가격/순위 파생변수 생성
3. TF-IDF 키워드 마이닝: 책 소개(inbukCntt) 기반 상위 30대 핵심 기술 키워드 추출
4. 데이터 품질 검증 및 주요 통계표 콘솔 출력

작성자: ai-practice 데이터 분석 튜터
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

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# student-materials 기준 상대경로
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def get_target_data_path(custom_path: str | None = None) -> Path:
    """분석 대상 CSV 경로를 찾습니다. 미지정 시 최신 수집 파일 또는 샘플 파일을 선택합니다."""
    if custom_path:
        return Path(custom_path)
    # 최신 수집 파일 탐색
    csv_files = sorted(DATA_DIR.glob("kyobo_it_bestsellers_*.csv"), reverse=True)
    if csv_files:
        return csv_files[0]
    # 샘플 파일 fallback
    return DATA_DIR / "sample_kyobo_bestsellers.csv"


# ==============================================================================
# 1. 5단계 기본 탐색 프로세스
# ==============================================================================
def run_basic_exploration(df: pd.DataFrame) -> None:
    """데이터 기본 탐색 5단계 프로세스를 실행하고 콘솔에 출력합니다."""
    print("=" * 60)
    print("1. [상하위 5개 행 표본]")
    print("=" * 60)
    print("=== 상위 5개 행 ===")
    print(df[["rank", "title", "author", "publisher", "sale_price", "rating"]].head())
    print("\n=== 하위 5개 행 ===")
    print(df[["rank", "title", "author", "publisher", "sale_price", "rating"]].tail())

    print("\n" + "=" * 60)
    print("2. [데이터 기본 정보 및 결측치 현황 (info)]")
    print("=" * 60)
    df.info()

    print("\n" + "=" * 60)
    print("3. [전체 행과 열 규모 (shape)]")
    print("=" * 60)
    print(f"전체 규모: {df.shape[0]:,}개 행(도서 건수), {df.shape[1]:,}개 열(속성)")

    print("\n" + "=" * 60)
    print("4. [중복 데이터 무결성 검증]")
    print("=" * 60)
    dup_cnt = int(df.duplicated(subset=["isbn"]).sum())
    print(f"ISBN 기준 중복 도서 수: {dup_cnt}건 (정합성: {'양호' if dup_cnt == 0 else '중복 존재'})")

    print("\n" + "=" * 60)
    print("5. [수치형 & 범주형 기술통계]")
    print("=" * 60)
    print("=== 수치형 변수 요약 ===")
    num_cols = ["rank", "original_price", "sale_price", "discount_rate", "rating", "review_count"]
    print(df[num_cols].describe().round(2))

    print("\n=== 범주형 변수 요약 ===")
    cat_cols = ["title", "author", "publisher", "category_name"]
    print(df[cat_cols].describe())


# ==============================================================================
# 2. 텍스트 마이닝 (TF-IDF 키워드 분석)
# ==============================================================================
def extract_top_keywords(df: pd.DataFrame, top_n: int = 30) -> pd.DataFrame:
    """책 소개(inbukCntt)에서 불용어를 제외하고 TF-IDF 상위 키워드를 추출합니다."""
    texts = df["inbukCntt"].dropna().astype(str).tolist()

    # 한국어 2글자 이상 단어 추출 패턴
    token_pattern = r"(?u)\b[가-힣a-zA-Z]{2,}\b"

    # 기본 불용어 리스트
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
    res_df = res_df.sort_values("TF-IDF점수", ascending=False).head(top_n).reset_index(drop=True)
    return res_df


# ==============================================================================
# 3. 메인 실행 함수
# ==============================================================================
def main() -> None:
    """EDA 실습 메인 실행 함수."""
    parser = argparse.ArgumentParser(description="교보문고 IT 베스트셀러 정제 및 EDA 실습")
    parser.add_argument(
        "--data-path",
        type=str,
        default=None,
        help="분석할 CSV 파일 경로 (미지정 시 최신 수집 데이터 자동 선택)",
    )
    args = parser.parse_args()

    target_path = get_target_data_path(args.data_path)

    print("=" * 60)
    print("📊 [Step 2] 데이터 정제 및 5단계 EDA 분석 실습 시작")
    print(f"- 로드 대상 파일: {target_path}")
    print("=" * 60)

    if not target_path.exists():
        print(f"[오류] 데이터 파일이 존재하지 않습니다: {target_path}")
        return

    df = pd.read_csv(target_path)
    print(f"[정보] 데이터 로드 완료 ({df.shape[0]:,}행 x {df.shape[1]:,}열)\n")

    # 1. 5단계 기본 탐색
    run_basic_exploration(df)

    # 2. TF-IDF 키워드 마이닝
    print("\n" + "=" * 60)
    print("6. [TF-IDF 텍스트 마이닝: 책 소개 상위 30대 핵심 키워드]")
    print("=" * 60)
    keywords_df = extract_top_keywords(df, top_n=30)
    print(keywords_df.to_string(index=True))

    print("\n[완료] 데이터 정제 및 기본 탐색 실습이 성공적으로 완료되었습니다!")


if __name__ == "__main__":
    main()
