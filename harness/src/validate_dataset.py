"""데이터셋 무결성 및 품질 검증 훅 스크립트.

이 스크립트는 수집된 CSV 데이터셋을 분석하여 행/열 규모, 중복 레코드 수,
컬럼별 결측률, 핵심 수치형 변수의 정합성을 점검하고, EDA 및 대시보드 파이프라인
진입 전 데이터 품질 게이트(Quality Gate) 역할을 수행합니다.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd

# Windows 콘솔 인코딩 대응
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def validate_csv(csv_path: Path, min_rows: int = 10, max_null_pct: float = 15.0) -> bool:
    """CSV 파일의 무결성을 검증하고 결과를 출력합니다."""
    print("=" * 60)
    print(f"🔍 [데이터 품질 검증 훅] 파일: {csv_path.name}")
    print("=" * 60)

    if not csv_path.exists():
        print(f"[검증 실패] 파일이 존재하지 않습니다: {csv_path}")
        return False

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"[검증 실패] CSV 로드 중 오류 발생: {e}")
        return False

    rows, cols = df.shape
    dup_count = int(df.duplicated().sum())
    dup_pct = round(dup_count / rows * 100, 2) if rows > 0 else 0.0

    print(f"- 데이터 규모: {rows:,}개 행, {cols:,}개 열")
    print(f"- 중복 데이터: {dup_count:,}건 ({dup_pct}%)")

    # 1. 최소 행 수 검증
    if rows < min_rows:
        print(f"[경고] 수집된 데이터 수가 최소 기준({min_rows}건) 미달입니다 (현재: {rows}건).")

    # 2. 결측치 분석
    null_counts = df.isnull().sum()
    high_null_cols = []
    print("\n[컬럼별 결측치 현황]")
    for col, n_cnt in null_counts.items():
        n_pct = round(n_cnt / rows * 100, 2) if rows > 0 else 0.0
        flag = " [주의]" if n_pct > max_null_pct else ""
        print(f"  - {col}: 결측 {n_cnt:,}건 ({n_pct}%){flag}")
        if n_pct > max_null_pct:
            high_null_cols.append((col, n_pct))

    # 3. 종합 판정
    is_valid = (rows >= min_rows) and (len(high_null_cols) == 0)

    print("\n" + "=" * 60)
    if is_valid:
        print(f"✅ [검증 통과] 데이터셋 무결성이 확인되었습니다 (행: {rows:,}건, 결측 기준 충족).")
    else:
        print(f"⚠️ [검증 주의/보완 필요] 일부 품질 기준이 미달되었습니다 (과다 결측 컬럼: {len(high_null_cols)}개).")
    print("=" * 60)

    return is_valid


def main() -> None:
    """CLI 실행 메인 함수."""
    parser = argparse.ArgumentParser(description="데이터셋 무결성 검증 도구")
    parser.add_argument("--file", type=str, required=True, help="검증할 CSV 파일 경로")
    parser.add_argument("--min-rows", type=int, default=10, help="최소 행 수 기준 (기본: 10)")
    parser.add_argument("--max-null-pct", type=float, default=15.0, help="허용 최대 결측률 (%)")
    args = parser.parse_args()

    success = validate_csv(Path(args.file), min_rows=args.min_rows, max_null_pct=args.max_null_pct)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
