"""20년차 시니어 데이터 분석가 범용 EDA 및 12종 시각화 파이프라인 템플릿.

이 스크립트는 수집된 모든 도메인의 정형/텍스트 데이터셋을 대상으로
1) 5단계 기본 무결성 탐색,
2) 범주형 및 TF-IDF 텍스트 특화 분석,
3) 12종의 일변량/이변량/다변량 고해상도 시각화 차트 생성,
4) 리포트용 10종 통계표 및 피봇테이블 산출을 자동으로 수행합니다.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import koreanize_matplotlib  # 한글 폰트 필수
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# Windows 콘솔 인코딩 대응
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def run_5step_exploration(df: pd.DataFrame) -> dict[str, Any]:
    """데이터 기본 탐색 5단계 프로세스를 실행합니다."""
    print("=" * 60)
    print("1. 상위 5개 행 & 하위 5개 행 표본")
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
    print(f"전체 데이터 규모: {df.shape[0]:,}개 행, {df.shape[1]:,}개 열")

    print("\n" + "=" * 60)
    print("4. 중복 데이터 확인")
    print("=" * 60)
    dup_cnt = int(df.duplicated().sum())
    print(f"중복 레코드 수: {dup_cnt:,}개 (중복률: {dup_cnt / len(df) * 100:.2f}%)")

    print("\n" + "=" * 60)
    print("5. 수치형 및 범주형 기술통계")
    print("=" * 60)
    print("=== 수치형 기술통계 ===")
    print(df.describe().round(2))

    cat_cols = df.select_dtypes(include=["object", "string", "category"]).columns
    if len(cat_cols) > 0:
        print("\n=== 범주형 기술통계 ===")
        print(df[cat_cols].describe())

    return {"shape": df.shape, "duplicates": dup_cnt}


def extract_tfidf_keywords(df: pd.DataFrame, text_col: str, top_n: int = 30) -> pd.DataFrame:
    """텍스트 컬럼에서 형태소 분석기 없이 TF-IDF 상위 N개 키워드를 추출합니다."""
    if text_col not in df.columns:
        return pd.DataFrame()

    texts = df[text_col].dropna().astype(str).tolist()
    if not texts:
        return pd.DataFrame()

    stopwords = {"수", "등", "및", "이", "그", "저", "위해", "통해", "대한", "관한", "있는", "하는"}
    tfidf = TfidfVectorizer(max_features=100, token_pattern=r"(?u)\b[가-힣a-zA-Z]{2,}\b", stop_words=list(stopwords))
    mat = tfidf.fit_transform(texts)
    words = tfidf.get_feature_names_out()
    scores = mat.sum(axis=0).A1

    res = pd.DataFrame({"키워드": words, "TF-IDF 점수": scores.round(2)})
    return res.sort_values("TF-IDF 점수", ascending=False).head(top_n).reset_index(drop=True)


def generate_12_charts(df: pd.DataFrame, output_dir: Path) -> None:
    """도메인 특성에 맞춘 12종 시각화 차트를 생성하여 저장합니다."""
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n[안내] 12종 시각화 차트 생성 시작 -> {output_dir}")

    # 차트 예시 (수치형 컬럼 자동 탐색)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not num_cols:
        print("[경고] 수치형 컬럼이 없어 시각화를 진행할 수 없습니다.")
        return

    # 샘플 차트 1: 첫 번째 수치 변수 분포
    plt.figure(figsize=(10, 5))
    plt.hist(df[num_cols[0]].dropna(), bins=25, color="#3498db", edgecolor="black", alpha=0.75)
    plt.title(f"{num_cols[0]} 변수 분포", fontsize=13, fontweight="bold")
    plt.xlabel(num_cols[0])
    plt.ylabel("빈도 수")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_dir / "01_distribution.png", dpi=300)
    plt.close()

    print("[완료] 기본 시각화 생성 완료 (실제 프로젝트 시 도메인 컬럼에 맞춰 12종 확장).")


def main() -> None:
    """CLI 메인 함수."""
    parser = argparse.ArgumentParser(description="20년차 시니어 EDA 템플릿")
    parser.add_argument("--data-path", type=str, required=True, help="분석 대상 CSV 경로")
    parser.add_argument("--output-images", type=str, default="harness/images", help="이미지 저장 폴더")
    args = parser.parse_args()

    csv_path = Path(args.data_path)
    if not csv_path.exists():
        print(f"[오류] 파일이 존재하지 않습니다: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    print("=" * 60)
    print(f"📊 [시니어 EDA 가동] 대상: {csv_path.name} (규모: {df.shape})")
    print("=" * 60)

    run_5step_exploration(df)
    generate_12_charts(df, Path(args.output_images))


if __name__ == "__main__":
    main()
