"""Chart.js 웹 대시보드용 범용 데이터 번들러 템플릿.

이 스크립트는 분석된 데이터셋(CSV)을 읽어와서 파생 변수 및 기술통계 메타데이터를
자동 계산한 후, 브라우저에서 CORS 제약 없이 로컬 파일(file://)로 바로 열 수 있도록
data.js 파일로 변환하여 저장합니다.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

# Windows 콘솔 인코딩 대응
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def export_dataframe_to_data_js(df: pd.DataFrame, output_js_path: Path, data_var_name: str = "DASHBOARD_DATA") -> None:
    """데이터프레임을 웹 대시보드용 data.js 파일로 패키징합니다."""
    output_js_path.parent.mkdir(parents=True, exist_ok=True)

    records = df.replace({np.nan: None}).to_dict(orient="records")

    metadata = {
        "generated_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_count": len(df),
        "columns": df.columns.tolist(),
        "summary": df.describe().round(2).to_dict() if not df.empty else {},
    }

    bundle = {
        "metadata": metadata,
        "items": records,
    }

    content = (
        f"// 범용 웹 대시보드 데이터 번들 (자동 생성)\n"
        f"// 항목 수: {len(df):,}건\n"
        f"window.{data_var_name} = "
        + json.dumps(bundle, ensure_ascii=False, indent=2)
        + ";\n"
    )

    output_js_path.write_text(content, encoding="utf-8")
    print("=" * 60)
    print(f"🎉 [번들 생성 완료] {output_js_path} (크기: {output_js_path.stat().st_size:,} bytes)")
    print("=" * 60)


def main() -> None:
    """CLI 메인 함수."""
    parser = argparse.ArgumentParser(description="대시보드 data.js 번들러")
    parser.add_argument("--data-path", type=str, required=True, help="입력 CSV 파일 경로")
    parser.add_argument("--out-js", type=str, default="harness/src/webapp/data.js", help="출력 data.js 경로")
    args = parser.parse_args()

    csv_path = Path(args.data_path)
    if not csv_path.exists():
        print(f"[오류] 파일이 없습니다: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    export_dataframe_to_data_js(df, Path(args.out_js))


if __name__ == "__main__":
    main()
